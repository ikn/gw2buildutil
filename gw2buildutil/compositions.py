import collections
import enum
import itertools
import math
import sys
import json
import pprint

from .build import Build, BoonTargets


class Configuration:
    def __init__ (
        self, target_buffs, target_uptime, overstack_uptime=None,
        uptime_comparison_tolerance=.01
    ):
        self.target_buffs = target_buffs
        self.target_uptime = target_uptime
        self.overstack_uptime = overstack_uptime
        self.uptime_comparison_tolerance = uptime_comparison_tolerance
        self.max_group_size = 5


class BuffUptime:
    def __init__ (self, config, buff, target, uptime):
        self.buff = buff
        self.target = target
        self._uptime = uptime
        self.uptime = min(config.target_uptime,
                          config.target_uptime if uptime is None else uptime)

    def __str__ (self):
        prefix = '' if self._uptime is None else f'{self.uptime * 100:.0f}% '
        return f'{prefix}{self.target.value.name} {self.buff.value.name}'

    def __repr__ (self):
        return f'BuffUptime<{str(self)}>'

    def uptime_for (self, target):
        if self.target == BoonTargets.PARTY:
            if target == BoonTargets.PARTY:
                return self.uptime
            else:
                return 0
        else: # self.target == BoonTargets.SQUAD
            return self.uptime

    @staticmethod
    def from_boon_uptime (boon_uptime, config):
        uptime = (None if boon_uptime.uptime_percent is None
                  else boon_uptime.uptime_percent / 100)
        return BuffUptime(config, boon_uptime.boon, boon_uptime.target, uptime)

class Role:
    _last_id = 0

    def __init__ (self, buff_uptimes, build_names):
        Role._last_id += 1
        self.id_ = str(Role._last_id)
        self.buff_uptimes = list(buff_uptimes)
        self.build_names = set(build_names)
        self.providing_roles = set()

    def __str__ (self):
        return ', '.join(str(uptime) for uptime in self.buff_uptimes)

    def __repr__ (self):
        return f'Role<{self.id_}: {str(self)}>'

    def _add_providing_role (self, role):
        self.providing_roles.add(role)

    def provides_buff (self, buff):
        return any(uptime.buff == buff for uptime in self.buff_uptimes)

    def uptime (self, buff, target):
        return max((uptime.uptime_for(target)
                    for uptime in self.buff_uptimes
                    if uptime.buff == buff), default=0)

    @staticmethod
    def _simplify_uptimes (uptimes):
        simplified_uptimes = collections.defaultdict(
            lambda: collections.defaultdict(lambda: 0))
        for uptime in uptimes:
            for target in BoonTargets:
                simplified_uptimes[uptime.buff][target] = max(
                    simplified_uptimes[uptime.buff][target],
                    uptime.uptime_for(target))
        return simplified_uptimes

    @staticmethod
    def _uptimes_equal (uptimes1, uptimes2, config):
        uptimes_lookup1 = Role._simplify_uptimes(uptimes1)
        uptimes_lookup2 = Role._simplify_uptimes(uptimes2)
        for buff in set(uptimes_lookup1).union(uptimes_lookup2):
            for target in BoonTargets:
                uptime1 = uptimes_lookup1[buff][target]
                uptime2 = uptimes_lookup2[buff][target]
                if abs(uptime1 - uptime2) > config.uptime_comparison_tolerance:
                    return False
        return True

    @staticmethod
    def _uptimes_greater (uptimes1, uptimes2, config):
        uptimes_lookup1 = Role._simplify_uptimes(uptimes1)
        uptimes_lookup2 = Role._simplify_uptimes(uptimes2)
        for buff in set(uptimes_lookup1).union(uptimes_lookup2):
            for target in BoonTargets:
                uptime1 = uptimes_lookup1[buff][target]
                uptime2 = uptimes_lookup2[buff][target]
                if uptime1 - uptime2 < -config.uptime_comparison_tolerance:
                    return False
        return True

    @staticmethod
    def list_from_builds (builds, config):
        builds_uptimes = {}
        for name, build in builds.items():
            if build.boon_notes is None:
                continue
            for i, variant in enumerate(build.boon_notes.boon_uptime_variants):
                builds_uptimes[(name, i)] = [
                    BuffUptime.from_boon_uptime(buff_uptime, config)
                    for buff_uptime in variant.boon_uptimes]

        eq_builds = collections.defaultdict(lambda: set())
        for (name1, uptimes1), (name2, uptimes2) in \
            itertools.combinations(builds_uptimes.items(), 2) \
        :
            if Role._uptimes_equal(uptimes1, uptimes2, config):
                eq_builds[name1].add(name2)
                eq_builds[name2].add(name1)

        builds_groups = {}
        for name in builds_uptimes:
            build_group = eq_builds[name]
            build_group.add(name)
            for eq_name in build_group:
                if eq_name in builds_groups:
                    builds_groups[eq_name].update(build_group)
                    break
            else:
                builds_groups[name] = build_group

        roles = [
            Role(builds_uptimes[next(iter(build_group))],
                 [name[0] for name in build_group])
            for build_group in builds_groups.values()]

        providing_roles = collections.defaultdict(lambda: set())
        for role1, role2 in itertools.permutations(roles, 2):
            if (role1 is not role2 and
                Role._uptimes_greater(
                    role1.buff_uptimes, role2.buff_uptimes, config)
            ):
                role2._add_providing_role(role1)

        return roles


class _SimpleComposition:
    def __init__ (self, config, group1, group2):
        self._config = config
        self.group1 = list(group1)
        self.group1_counter = collections.Counter(self.group1)
        self.group2 = list(group2)
        self.group2_counter = collections.Counter(self.group2)
        self._roles_counter = collections.Counter(self.roles)

    def __str__ (self):
        return ' | '.join(' '.join(role.id_ for role in group)
                         for group in (self.group1, self.group2))

    def __repr__ (self):
        return f'_SimpleComposition<{str(self)}>'

    @property
    def roles (self):
        return self.group1 + self.group2

    def __eq__ (self, other):
        return self._roles_counter == other._roles_counter

    def __len__ (self):
        return len(self.group1) + len(self.group2)

    def provides (self, other):
        remaining_roles = self._roles_counter - other._roles_counter
        remaining_other_roles = other._roles_counter - self._roles_counter

        # match roles with only 1 providing role
        for other_role in remaining_other_roles:
            our_providing_roles = [role for role in remaining_roles
                                   if role in other_role.providing_roles]
            if len(our_providing_roles) == 1:
                # `counter[i] -=` can produce negative counts
                reduction = min(remaining_other_roles[other_role],
                                remaining_roles[our_providing_roles[0]])
                remaining_roles[our_providing_roles[0]] -= reduction
                remaining_other_roles[other_role] -= reduction

        remaining_roles_seq = list(remaining_roles.elements())
        remaining_other_roles_seq = list(remaining_other_roles.elements())
        if len(remaining_roles_seq) < len(remaining_other_roles_seq):
            return False

        # check all possible reorderings to match the rest
        for roles_ordering in itertools.permutations(
            remaining_roles_seq, len(remaining_other_roles_seq)
        ):
            if (all(role in other_role.providing_roles
                    for role, other_role
                    in zip(roles_ordering, remaining_other_roles_seq))
            ):
                return True
        return False

    def uptime (self, buff):
        result = []
        for group in (1, 2):
            own_group = self.group1 if group == 1 else self.group2
            own_group_uptime = sum(
                role.uptime(buff, BoonTargets.PARTY)
                for role in own_group)
            off_group = self.group2 if group == 1 else self.group1
            off_group_uptime = sum(
                role.uptime(buff, BoonTargets.SQUAD)
                for role in off_group)
            result.append(own_group_uptime + off_group_uptime)
        return result

    def overstack (self):
        if self._config.overstack_uptime is None:
            return False

        for buff in self._config.target_buffs:
            for uptime in self.uptime(buff):
                if uptime >= self._config.overstack_uptime:
                    return True

        return False


    @staticmethod
    def empty (config):
        return _SimpleComposition(config, [], [])


class Composition:
    def __init__ (self, comps):
        self.compositions = list(comps)

    @property
    def roles (self):
        return self.compositions[0].roles

    def __str__ (self):
        return ' '.join('[' + str(comp) + ']' for comp in self.compositions)

    def __repr__ (self):
        return f'Composition<{str(self)}>'


def _simplify_compositions (config, comps):
    comps = list(comps)

    # group together comps that use the same roles
    grouped_comps = []
    i = 0
    while i < len(comps):
        comp1 = comps[i]
        groupings = [comp1]
        grouped_comps.append(groupings)
        j = i + 1
        while j < len(comps):
            comp2 = comps[j]
            if comp2 == comp1:
                groupings.append(comp2)
                comps.pop(j) # now we can skip over comp2 in the outer loop
            else:
                j += 1
        i += 1

    # filter out comps which are the same as another comp, with roles replaced
    # with other roles with strictly better uptimes (eg. don't use an
    # inspiration chrono when you can use a firebrand)

    # sort so we process smaller comps first, which can be compared faster
    grouped_comps.sort(key=lambda groupings: len(groupings[0]))
    simplified_grouped_comps = []
    for new_groupings in grouped_comps:
        if new_groupings[0].overstack():
            continue

        j = 0
        while j < len(simplified_grouped_comps):
            existing_groupings = simplified_grouped_comps[j]
            if new_groupings[0].provides(existing_groupings[0]):
                break
            elif existing_groupings[0].provides(new_groupings[0]):
                simplified_grouped_comps.pop(j)
            else:
                j += 1
        else:
            simplified_grouped_comps.append(new_groupings)

    for groupings in simplified_grouped_comps:
        normalised_groupings = []
        for comp in groupings:
            for existing_comp in normalised_groupings:
                is_same = (
                    comp.group1_counter == existing_comp.group1_counter and
                        comp.group2_counter == existing_comp.group2_counter)
                is_mirrored = (
                    comp.group1_counter == existing_comp.group2_counter and
                    comp.group2_counter == existing_comp.group1_counter)
                if is_same or is_mirrored:
                    break
            else:
                normalised_groupings.append(comp)
        yield Composition(normalised_groupings)


# base_comp must contain exactly 1 grouping
# target_uptime has tolerance applied
def _generate_compositions_for_buff (
    base_comp, roles_group1, roles_group2, buff, config
):
    uptime_group1, uptime_group2 = base_comp.uptime(buff)
    needed_group1 = config.target_uptime - uptime_group1
    allowed_group1 = (1000 if config.overstack_uptime is None
                      else config.overstack_uptime - uptime_group1)
    needed_group2 = config.target_uptime - uptime_group2
    allowed_group2 = (1000 if config.overstack_uptime is None
                      else config.overstack_uptime - uptime_group2)
    if ((needed_group1 < config.uptime_comparison_tolerance and
         needed_group2 < config.uptime_comparison_tolerance)
    ):
        yield base_comp
        return

    # when recurring, we don't pass through roles we've already checked, because
    # that will just produce reorderings of the same compositions
    for role_index, role in enumerate(roles_group1):
        provides_group = role.uptime(buff, BoonTargets.PARTY)
        provides_off_group = role.uptime(buff, BoonTargets.SQUAD)
        max_usable_group = (0 if provides_group == 0
                            else math.ceil(needed_group1 / provides_group))
        max_usable_off_group = (
            0 if provides_off_group == 0
            else math.ceil(needed_group2 / provides_off_group))
        max_allowed = min(
            config.max_group_size - len(base_comp.group1),
            # doesn't catch cases where we overstack on a different buff, but
            # all comps are checked again for overstack at the end
            (config.max_group_size if provides_group == 0
             else int(allowed_group1 / provides_group)),
            (config.max_group_size if provides_off_group == 0
             else int(allowed_group2 / provides_off_group)))
        max_to_use = min(max_allowed,
                         max(max_usable_group, max_usable_off_group))
        for num_used in range(1, max_to_use + 1):
            comp = _SimpleComposition(config,
                                      base_comp.group1 + [role] * num_used,
                                      base_comp.group2)
            yield from _generate_compositions_for_buff(
                comp, roles_group1[role_index + 1:], roles_group2, buff, config)

    # if groups are identical, adding to group 2 just produces mirrored comps
    if base_comp.group1_counter == base_comp.group2_counter:
        return

    for role_index, role in enumerate(roles_group2):
        provides_group = role.uptime(buff, BoonTargets.PARTY)
        provides_off_group = role.uptime(buff, BoonTargets.SQUAD)
        max_usable_group = (0 if provides_group == 0
                            else math.ceil(needed_group2 / provides_group))
        max_usable_off_group = (
            0 if provides_off_group == 0
            else math.ceil(needed_group1 / provides_off_group))
        max_allowed = min(
            config.max_group_size - len(base_comp.group2),
            # doesn't catch cases where we overstack on a different buff, but
            # all comps are checked again for overstack at the end
            (config.max_group_size if provides_group == 0
             else int(allowed_group2 / provides_group)),
            (config.max_group_size if provides_off_group == 0
             else int(allowed_group1 / provides_off_group)))
        max_to_use = min(max_allowed,
                         max(max_usable_group, max_usable_off_group))
        for num_used in range(1, max_to_use + 1):
            comp = _SimpleComposition(config,
                                      base_comp.group1,
                                      base_comp.group2 + [role] * num_used)
            yield from _generate_compositions_for_buff(
                comp, roles_group1, roles_group2[role_index + 1:], buff, config)


def generate_compositions (roles, config):
    roles_by_buff = {buff: [role for role in roles if role.provides_buff(buff)]
                     for buff in config.target_buffs}
    def generate (target_buffs):
        if len(target_buffs) > 1:
            base_comps = generate(target_buffs[:-1])
        else:
            base_comps = [_SimpleComposition.empty(config)]
        for base_comp in base_comps:
            roles_for_buff = roles_by_buff[target_buffs[-1]]
            yield from _generate_compositions_for_buff(
                base_comp,
                roles_for_buff,
                roles_for_buff,
                target_buffs[-1],
                config)

    ordered_target_buffs = sorted(config.target_buffs,
                                  key=lambda buff: len(roles_by_buff[buff]))
    return _simplify_compositions(
        config, list(generate(list(ordered_target_buffs))))
