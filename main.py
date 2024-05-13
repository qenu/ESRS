# Evan Skill Rotation Simulator
# Version 0.21.EB final DMG adjust
# Author: Ba, Yuyu

from collections import Counter

from rich import print
from rich.console import Console
from rich.table import Table


class Skill:
    def __init__(
        self,
        *,
        damage: int = 0,
        decay: int = 1,
        cd: float = 0,
        timing: list[int] = [0],
    ):
        self.cooldown = cd
        self.base_damage = damage
        self.damage_decay = decay
        self.attack_timing = timing
        self.damage_ratio: list[int, int, float] = []

        prev_dmg = 0  # calculate decay
        prev_ms = 0
        for ms in timing:
            prev_dmg = (
                self.base_damage
                if prev_dmg == 0
                else prev_dmg * self.damage_decay
            )
            delay = ms - prev_ms
            self.damage_ratio.append(
                [
                    delay,
                    round(prev_dmg, 6),  # damage
                    round(prev_dmg / (1 if delay < 1 else delay), 6),  # ratio
                ]
            )
            prev_ms = ms


class SkillRetarded:
    def __init__(self, *, damages: list[int], timing: list[int], cd: float):
        self.damage_ratio = [[0, 0, 0]]
        prev_ms = 0
        for dmg, ms in zip(damages, timing):
            delay = ms - prev_ms
            self.damage_ratio.append(
                [delay, dmg, round(dmg / (1 if delay < 1 else delay), 6)]
            )
            prev_ms = ms
        self.cooldown = cd


class Evan:
    def __init__(self):
        self.item_cd_reduction = 0  # second int
        self.merc_cd_reduction = 0  # perc int
        self.damage_offset = 0

        self.low_health_target = False

        self.hyper_cd_tf = False
        self.hyper_cd_ed = False
        self.hyper_cd_wb = False
        self.hyper_ext_tf = False
        self.hyper_dmg_ed = False
        self.hyper_dmg_wb = False

        self.hexa_eb = 0
        self.hexa_ds = 0
        self.hexa_sm = 0
        self.hexa_er = 0
        
        self.continul_final_dmg = 0

        self.skills: dict[Skill] = {}

    def item_cd(self, cd) -> "Evan":
        self.item_cd_reduction = cd
        return self

    def merc_cd(self, cd) -> "Evan":
        self.merc_cd_reduction = cd
        return self

    def resolve_cooldown(
            self, cooldown, hyper: bool = False
        ) -> int | float:
        cd = round(
            cooldown
            * (0.75 if hyper else 1)
            * (100 - self.merc_cd_reduction)
            / 100,
            4,
        )
        if (cd - self.item_cd_reduction) > 10:
            cd -= self.item_cd_reduction
        elif cd > 10:
            cd = 10 * (1 - (self.item_cd_reduction - (cd - 10)) * 0.05)
        else:
            cd = cd * (1 - (self.item_cd_reduction * 0.05))
        return max(cd, 5)

    @property
    def status(self) -> None:
        console = Console()
        status = Table(
            title="Current Configuration",
            title_justify="center",
            title_style="bold",
        )
        status.add_column("Name", justify="left", style="bold cyan")
        status.add_column("Status", justify="right", style="bold green")
        status.add_row("Item Reduction", f"{self.item_cd_reduction} sec")
        status.add_row("Mercedes Reduction", f"{self.merc_cd_reduction}%")
        status.add_row("Adjusted Damage", f"[red]{self.damage_offset:}%[/red]")
        status.add_row(
            "Low Health Target",
            "Yes" if self.low_health_target else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Thunder Flash CD",
            "Yes" if self.hyper_cd_tf else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Earth Dive CD",
            "Yes" if self.hyper_cd_ed else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Wind Breath CD",
            "Yes" if self.hyper_cd_wb else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Thunder Flash Ext",
            "Yes" if self.hyper_ext_tf else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Earth Dive Damage",
            "Yes" if self.hyper_dmg_ed else "[red]No[/red]",
        )
        status.add_row(
            "Hyper: Wind Breath Damage",
            "Yes" if self.hyper_dmg_wb else "[red]No[/red]",
        )
        status.add_row("Hexa: Elemental Barrage", f"Lv. {self.hexa_eb}")
        status.add_row("Hexa: Dragon Slam", f"Lv. {self.hexa_ds}")
        status.add_row("Hexa: Elemental Radiance", f"Lv. {self.hexa_er}")
        status.add_row("Hexa: Spiral of Mana", f"Lv. {self.hexa_sm}")
        console.print(status)
    
    @property
    def skill_info(self) -> None:
        # Skill Config
        for k, v in self._get_data.items():
            print(f"{k:^50}")
            print(
                f"{'millisec':^10} | {'damage':^10}"
                f" | {'ratio':^10} | {'cum':^10}"
            )
            print(f"{'':-^50}")
            cum_ms = 0
            for _ in v:
                if k == self.retard and _["damage"] == 0:
                    continue
                cum_ms += _["ms"]
                print(
                    f"{_['ms']:>10,} | {_['damage']:>10,}"
                    f" | {_['ratio']:>10,.2f} | {cum_ms:>10}"
                )
            print(f"{'':-^50}")
            print(f"Cooldown: {self.skills[k].cooldown} sec\n")

    @property
    def update_skill(self) -> "Evan":
        def get_hexa_dmg(hexa):
            if not hexa:
                return 1
            if hexa == 30:
                return 1.6
            return  1.1 + (hexa / 10 + 1) * 0.15 + hexa % 10 * 0.01

        def get_hexa_cooldown(hexa):
            if not hexa:
                return 60
            for n, v in enumerate(range(25, 0, -8)):
                if hexa > v:
                    return 40 + n * 5
                        
        # Thunder Flash
        self.skills["Thunder Flash"] = Skill(
            damage=1300 * (10 if self.hyper_ext_tf else 9) * 2.2,
            decay=0.4,
            cd=self.resolve_cooldown(8, self.hyper_cd_tf),
            timing=[480, 840, 1200, 1560, 1920],
        )

        # Earth Dive
        self.skills["Earth Dive"] = Skill(
            damage=1000 * 10 * 2.2,
            decay=0.5,
            cd=self.resolve_cooldown(8, self.hyper_cd_ed),
            timing=[0, 960, 1440, 1920],
        )

        # Wind Breath
        self.skills["Wind Breath"] = Skill(
            damage=(
                216 + (151 if self.hyper_dmg_wb else 66)
                if self.low_health_target
                else 216
            )
            * 6
            * 2.2,
            cd=self.resolve_cooldown(10, self.hyper_cd_wb),
            timing=[0, 360, 720, 1080, 1440, 1800, 2160, 2520],
        )

        # Dragon Slam
        self.skills["Dragon Slam"] = Skill(
            damage=1265 * 7 * get_hexa_dmg(self.hexa_ds),
            cd=self.resolve_cooldown(20),
            timing=[80, 200, 500, 800, 1280, 1680],
        )

        eb_timing = [660, 1890, 2450, 3300]
        ewb_timing = sorted(
            eb_timing
            + [
                1200,
                1440,
                1680,
                1920,
                2160,
                2400,
                2640,
                2880,
                3120,
                3360,
                3600,
                3840,
                4080,
                4320,
                4560,
                4800,
            ]
        )

        def eb_final_damage(ms):
            if ms < eb_timing[0]:
                return 1
            for _ in eb_timing:
                if ms < _:
                    return 1 + (eb_timing.index(_) + 1 * 0.05)
            return 1 + (len(eb_timing) * 0.05)

        self.skills["Elemental Wyrm Breath"] = SkillRetarded(
            damages=[
                (
                    round(
                        1705
                        * 8
                        * get_hexa_dmg(self.hexa_ds)
                        * eb_final_damage(_),
                        2,
                    )
                    if _ in eb_timing
                    else round(
                        1320
                        * 7
                        * get_hexa_dmg(self.hexa_ds)
                        * eb_final_damage(_),
                        2,
                    )
                )
                for _ in ewb_timing
            ],
            timing=ewb_timing,
            cd=self.resolve_cooldown(get_hexa_cooldown(self.hexa_eb)),
        )

        # Ludicrous Speed (insert to DS first hit)
        head = self.skills["Dragon Slam"].damage_ratio[0]
        ms = head[0]
        cum_dmg = 330 * 3 * get_hexa_dmg(self.hexa_ds) * 9
        update_dmg = head[1] + cum_dmg
        update_ratio = round(update_dmg / (1 if ms < 1 else ms), 6)
        self.skills["Dragon Slam"].damage_ratio[0] = [
            ms,
            update_dmg,
            update_ratio,
        ]

        # Continual Skills 
        mana_burst = round(((555 + 625) * 4 * 2.2) / 1.17, 4)
        return_flame = round(150 * 2.2 / 0.45, 4)
        magic_debris = round((120 + 200) * 2.2 / 0.4, 4)
        spiral_mana = round(265 * 3 * get_hexa_dmg(self.hexa_sm) / 0.36, 4)
        self.continual_dps = sum([mana_burst, return_flame, magic_debris, spiral_mana])

        # Elemental Radiance
        call_ambulance_but_not_for_me = 1045 * 552 * get_hexa_dmg(self.hexa_er)
        self.elemental_radiance = call_ambulance_but_not_for_me

        self.time_limit = max([_.cooldown for _ in self.skills.values()])
        return self

    @property
    def skill_weights(self):
        result = {}
        for k, v in self._get_data.items():
            for n, item in enumerate(v):
                result[f"{k} {n+1}"] = item["ratio"]
        return sorted(result.items(), key=lambda x: x[1], reverse=True)[:-1]

    @property
    def _get_data(self) -> dict:
        return {
            k: [
                {"ms": _[0], "damage": _[1], "ratio": _[2]}
                for _ in v.damage_ratio
            ]
            for k, v in self.skills.items()
        }

    @property
    def retard(self) -> str:
        return "Elemental Wyrm Breath"

    def rotation(self):
        data = self._get_data

        virtual_t = 0
        skill_queue = [] 
        skill_step = Counter()  # skills in use
        skill_finish = []
        skill_cooldown = {}  # sec
        sleep_time: list = []
        retard = self.retard
        limit = self.time_limit * 1000

        def retard_soon():
            if retard not in skill_cooldown:
                return False
            remain_cd = skill_cooldown.get(retard, 0) - virtual_t
            partial_cd = self.skills["Dragon Slam"].cooldown * 1000 #+ 1680
            if remain_cd < partial_cd:
                # print("waiting")
                return True
            return False

        def retard_ready():
            # retard ready check 
            if retard in list(
                set(list(skill_step) + list(skill_cooldown) + skill_finish)
            ):
                return False
            return True

        def close_skill(skill: str, skill_queue: list, skill_step: Counter):
            # macro for skill closing
            if skill in skill_queue:
                idx = skill_queue.index(skill)
                skill_queue[idx] = (skill_queue[idx], skill_step[skill])
            del skill_step[skill]

        while virtual_t < limit:

            # releasing skill when cooldown passed 
            cd_ready = [
                k 
                for k, v in skill_cooldown.items() 
                if v <= virtual_t
                ]
            for skill in cd_ready:
                skill_cooldown.pop(skill, None)
                close_skill(skill, skill_queue, skill_step)

                if skill in skill_finish:
                    skill_finish.remove(skill)

            # retard extender to attach skill in skill queue
            if skill_queue and \
            skill_queue[-1] == "Dragon Slam" and \
                retard_ready():
                skill_queue.append(retard)
                skill_step[retard] += 1
                skill_cooldown[retard] = virtual_t + \
                    self.skills[retard].cooldown * 1000
                continue

            skill_weighted = {
                k: v[skill_step.get(k, 0)]["ratio"]
                for k, v in data.items()
                if k not in skill_finish
            }

            # Dragon Slam waits for Daddy 
            if "Dragon Slam" in skill_weighted.keys() and retard_soon():
                del skill_weighted["Dragon Slam"]

            if skill_weighted:
                # if slept once then trigger awake
                if sleep_time and len(sleep_time[-1]) == 1:
                    sleep_time[-1].append(virtual_t)
                step_next = max(skill_weighted, key=skill_weighted.get)

                # if skill is not in skill_queue
                if not skill_queue or step_next not in skill_step.keys():
                    skill_queue.append(step_next)
                    skill_cooldown[step_next] = virtual_t + \
                        self.skills[step_next].cooldown * 1000

                # step_next skill used time
                step_next_time = data[step_next][skill_step[step_next]]["ms"]
                virtual_t = virtual_t + step_next_time

                # insert step_next delay to leading skills
                if step_next in (cd_list := list(skill_cooldown.keys())):
                    idx = cd_list.index(step_next) + 1
                    for skill in cd_list[idx:]:
                        skill_cooldown[skill] += step_next_time

                # close skill if done with steps 
                skill_step[step_next] += 1
                if skill_step[step_next] == len(data[step_next]):
                    skill_finish.append(step_next)
                    close_skill(step_next, skill_queue, skill_step)
            else:
                # sleep if skill is mia
                if not sleep_time or len(sleep_time[-1]) == 2:
                    sleep_time.append([virtual_t])
                virtual_t += 1

        # back port remaining skill steps to skill_queue
        for k, v in skill_step.items():
            idx = skill_queue.index(k)
            skill_queue[idx] = (skill_queue[idx], v)
 
        # cumulative damage for each skill_queue
        damage_done = [
            round(sum(foo[1] 
            for foo in self.skills[_[0]].damage_ratio[: _[1]]), 3)
            for _ in skill_queue
            if isinstance(_, tuple)
        ]

        # cleanup retard hits
        skill_queue = [
            [_[0], _[1] - 1] 
            if _[0] == retard 
            else _ for _ in skill_queue
            ]

        # cleanup sleep
        if sleep_time and len(sleep_time[-1]) == 1:
            sleep_time.pop(-1)

        return {
            "queue": skill_queue,
            "damage": damage_done,
            "time": virtual_t,
            "sleep": [_[1]-_[0] for _ in sleep_time],
            "dps": round(sum(damage_done)/virtual_t, 4),
        }
    
    def rotation_refine(self, data):
        skill_queue = data['queue']
        sleep = data["sleep"]
        virtual_t = 0
        cooldown_check = {}
        refined_queue = []

        # zodiac_burst = "Zodiac Burst"
        zodiac_burst = True
        # Elemental Barrage
        elemental_barrage = 0

        def append_skill(queue, name, hit, damage, init, used, cooldown):
            foo = {}
            foo["name"] = name
            foo["hit"] = hit
            foo["damage"] = damage
            foo["init"] = init
            foo["used"] = used
            foo["done"] = init + used
            foo["cd"] = cooldown
            queue.append(foo)

        def get_hexa_dmg(hexa):
            if not hexa:
                return 1
            if hexa == 30:
                return 1.6
            return  1.1 + (hexa / 10 + 1) * 0.15 + hexa % 10 * 0.01
        
        def calculate_eb_avg_fd(CD, totaltime):

            CD *= 1000
            totaltime *= 1000

            eb_times = totaltime // CD
            eb_times_dmg = 2245 * eb_times

            left_time = totaltime % CD
            damage_percentages = [
                (660, 0.05),
                (1890, 0.10),
                (2450, 0.15),
                (3300, 0.20),
                (13300, 0),
                (CD, 0),
            ]
            left_time_dmg = 0

            if left_time > 0:
                for i in range(len(damage_percentages) - 1):
                    current_time, current_percentage = damage_percentages[i]
                    next_time, next_percentage = damage_percentages[i + 1]     

                    if left_time >= next_time :   

                        left_time_dmg += current_percentage * (next_time - current_time)
                    else:
                        left_time_dmg += current_percentage * ((next_time - current_time) - (next_time - left_time))
                        print(((next_time - current_time) - (next_time - left_time)))
                        break
            
            average_damage = (eb_times_dmg + left_time_dmg) / totaltime
            return (1 + average_damage) * 100
        
        # Elemental Radiance
        append_skill(
            refined_queue, 
            "Elemental Radiance", 
            552, 
            1045 * 552 * get_hexa_dmg(self.hexa_er) * 1.2, # elemental_barrage
            virtual_t,
            780,
            round(self.resolve_cooldown(180) * 1000)
            )
        virtual_t += 780

        for item in skill_queue:
            if cooldown_check.get(item[0], 0) > virtual_t and sleep:
                t = 1
                sleep_cum = sleep[0]
                sleep = {}
                while cooldown_check.get(item[0], 0) > (sleep_cum + virtual_t):
                    t+=1
                    if t > len(sleep):
                        break
                    sleep_cum = sum(sleep[0:t])
                append_skill(refined_queue, "sleep", 0, 0, virtual_t, 0, 0)

            cum_damage = 0
            cum_time = 0
            name = item[0]
            hits = item[1]
            skill: Skill = self.skills[name]
            
            if name == self.retard:
                elemental_barrage = virtual_t + 13300

            for _ in range(hits):
                damage_ratio = skill.damage_ratio[_+1] if name == self.retard else skill.damage_ratio[_]
                virtual_t += damage_ratio[0]
                eb_ext = 1.2 if virtual_t <= elemental_barrage and name is not self.retard else 1
                cum_damage += damage_ratio[1] * eb_ext

            append_skill(
                refined_queue,
                name,
                hits,
                cum_damage,
                virtual_t,
                cum_time,
                int((skill.cooldown * 1000) + virtual_t)
                )
            virtual_t += cum_time

            if zodiac_burst and name == "Elemental Wyrm Breath":
                zodiac_burst = False
                cum_damage = 5400 * 15 * 5 * 1.2
                cum_damage += 1440 * 6 * 9 * 3 * 1.2
                cum_damage += 1440 * 6 * 9 * 13
                append_skill(
                    refined_queue,
                    "Zodiac Burst",
                    17,
                    cum_damage,
                    virtual_t,
                    0,
                    round(self.resolve_cooldown(360) * 1000)
                )
            
        # return refined_queue
    
        time = data["time"]
        damage_done = [_["damage"] for _ in refined_queue if _["name"] not in ["Elemental Radiance", "Zodiac Burst"]]

        _timeused = f"{round(time/1000, 3)} / {self.time_limit}"
        timeused = f"[bold green]{_timeused}[/bold green] sec"

        eb_avg_fd = calculate_eb_avg_fd(self.skills["Elemental Wyrm Breath"].cooldown, self.time_limit)
        contunual_fdfix = f"{eb_avg_fd:,.2f}%"
 
        continual = f"{(self.continual_dps * eb_avg_fd / 100) * time / 1000:,.2f}%"
        rotation_cum = f"{sum(damage_done):,.2f}%"
        _elemental_radiance = f"{sum([_['damage'] for _ in refined_queue if _['name'] == 'Elemental Radiance']):,.2f}%"
        _zodiac_burst = f"{sum([_['damage'] for _ in refined_queue if _['name'] == 'Zodiac Burst']):,.2f}%"
        _total_dmg = round(
            (sum([_["damage"] for _ in refined_queue]) + \
            (self.continual_dps * eb_avg_fd / 100) * \
            time / 1000) * (1 + self.damage_offset/100), 3
            )
        total_dmg = f"{_total_dmg:,.2f}%"

        
        burst_dps = f"{sum([_['damage'] for _ in refined_queue if _['name'] in ['Elemental Radiance', 'Zodiac Burst']])/time*1000:,.2f}%/s"
        dps = f"{sum(damage_done)/time*1000:,.2f}%/s"
        continual_dps = f"{(self.continual_dps * eb_avg_fd / 100):,.2f}%/s"
        cum_dps = f"{_total_dmg / time * 1000:,.2f}%/s"

        first_line = f"Time used:              {timeused}\n"
        align = len(_timeused) + 4
        
        print(
            f"{first_line}"
            f"Continual Final Dmg:    {contunual_fdfix:>{align}}\n"
            f"{'':=<{align+24}}\n"
            f"Continual:              {continual:>{align}}\n"
            f"Rotation Cumulative:    {rotation_cum:>{align}}\n"
            f"Elemental Radiance:     {_elemental_radiance:>{align}}\n"
            f"Zodiac Burst:           {_zodiac_burst:>{align}}\n"
            f"[red bold]Total Damage:[/red bold]           {total_dmg:>{align}}\n"
            f"{'':=<{align+24}}\n"            
            f"Continual DPS:          {continual_dps:>{align}}\n"
            f"Rotation DPS:           {dps:>{align}}\n"
            f"Burst DPS:              {burst_dps:>{align}}\n"
            f"{'':=<{align+24}}\n"
            f"[red bold]Cumulative DPS:[/red bold]         {cum_dps:>{align}}\n"
        )


if __name__ == "__main__":
    evan = Evan()

    evan.low_health_target = True

    evan.hyper_cd_tf = True
    evan.hyper_cd_ed = True
    evan.hyper_cd_wb = True
    evan.hyper_ext_tf = True
    evan.hyper_dmg_ed = True
    evan.hyper_dmg_wb = True

    # yuyu
    evan.merc_cd_reduction = 6

    evan.item_cd_reduction = 2 
    evan.damage_offset = 0
    evan.hexa_ds = 30
    evan.hexa_eb = 30
    evan.hexa_er = 30
    evan.hexa_sm = 30

    # sib
    # evan.merc_cd_reduction = 5
    # evan.item_cd_reduction = 5

    # rando
    # evan.merc_cd_reduction = 0
    # evan.item_cd_reduction = 0
    # evan.damage_offset = 3.7

    evan.skills["Cooldown Foddler"] = Skill(
        damage=0, 
        timing=[0],
        cd=167.2,
    )
    evan.update_skill
    # evan.status
    data = evan.rotation()
    refined = evan.rotation_refine(data)
    # print(f"{round(sum(data['damage'])/data['time'], 4)}%")
    # print(evan.skill_weights)

