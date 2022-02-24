import io, math
from tokenize import String
from typing import List, Tuple

from matplotlib import projections
from visualise_graph import Graph, dijsktra
import time

car_count = 1
simlen = 1


class Skill:
    type = ""
    level = 0

    def __init__(self, line: str):
        splt = line.split(' ')
        self.type = splt[0]
        self.level = int(splt[1].strip())

    def __repr__(self) -> str:
        return self.type + " " + str(self.level)


class Contributor:
    name: str = ""
    skillcount: int = 0
    skills: List[Skill] = []
    project = None

    def __init__(self, line):
        splt = line.split(' ')
        self.name = splt[0]
        self.skillcount = int(splt[1].strip())
        self.project = None

    def __repr__(self):
        return self.name

    def setProject(self, project):
        self.project = project

    def has_project(self):
        return self.project is not None

    def get_skill(self, skilltype: str) -> Skill:
        for skill in self.skills:
            if skill.type == skilltype:
                return skill

        return None

    def has_skill(self, skillReq: Skill, mentoringAvailable=False):
        for skill in self.skills:
            if skill.type == skillReq.type:
                return skill.level >= skillReq.level or (mentoringAvailable and skill.level == skillReq.level - 1)

        return False

    def has_skill_up(self, skillReq: Skill, mentoringAvailable=False):
        for skill in self.skills:
            if skill.type == skillReq.type:
                return skill.level == skillReq.level or (mentoringAvailable and skill.level == skillReq.level - 1)

        return False


schedule = []

class Schedule:
    projectname = ""
    workers = []

    def __init__(self, projectname, workers):
        self.projectname = projectname
        self.workers = workers

    def add_worker(self, worker):
        self.workers.append(worker)

class Role:
    skill: Skill = None
    contributor: Contributor = None
    mentoredBy: Contributor = None

    def __init__(self, skill: Skill, contributor: Contributor):
        self.skill = skill
        self.contributor = contributor
        self.mentoredBy = None

    def __repr__(self) -> str:
        return str(self.contributor) + " -> " + str(self.skill)

    def add_mentor(self, mentor: Contributor):
        self.mentoredBy = mentor

    def needs_mentoring(self) -> bool:
        currentSkill = self.contributor.get_skill(self.skill.type)

        return self.skill.level == currentSkill.level - 1


PROJECT_OPEN = "open"
PROJECT_IN_PROGRESS = "in_progress"
PROJECT_DONE = "done"


class Project:
    name: str = ""
    duration: int = 0
    score: int = 0
    best_before: int = 0
    skillcount: int = 0
    neededSkills: List[Skill] = []
    status: str = PROJECT_OPEN
    roles: List[Role] = []
    days_left: int = 0

    def __init__(self, line: str):
        splt = line.split(' ')
        self.name = splt[0]
        self.duration = int(splt[1].strip())
        self.score = int(splt[2].strip())
        self.best_before = int(splt[3].strip())
        self.skillcount = int(splt[4].strip())
        self.status = PROJECT_OPEN
        self.roles = []
        self.days_left = self.duration

    def __repr__(self) -> str:
        return self.name + " (" + self.status + ")"

    def start(self, roles: List[Role]):
        self.days_left = self.duration
        self.status = PROJECT_IN_PROGRESS
        self.roles = roles

        for role in self.roles:
            role.contributor.setProject(self)
        
    def worth(self, currentDay: int) -> int:
        if self.duration + currentDay > self.best_before:
            rem_days = self.best_before - currentDay
            if rem_days >= self.duration:
                return self.score

            return max(self.score - (self.duration - rem_days), 0)

        return self.score

    def is_in_progress(self):
        return self.status == PROJECT_IN_PROGRESS

    def is_open(self):
        return self.status == PROJECT_OPEN

    def progress(self, days: int):
        self.days_left -= days

        if self.days_left == 0:
            self.status = PROJECT_DONE

            print("Finishing " + str(self))
            workers = []
            for role in self.roles:
                workers.append(role.contributor.name)
            schedule.append(Schedule(
                self.name,
                workers
            ))

            for role in self.roles:
                if role.contributor.has_skill_up(role.skill, True):
                    role.contributor.get_skill(role.skill.type).level += 1
                role.contributor.setProject(None)


class RoleComposition:
    project: Project = None
    roles: List[Role] = []

    def __init__(self, project: Project):
        self.project = project
        self.roles = []

    def __repr__(self) -> str:
        return str(self.project) + " -> " + str(self.roles)

    def __eq__(self, other) -> bool:
        roles = self.roles.copy()
        roles.sort(key=lambda x : x.contributor.name)

        otherroles = other.roles.copy()
        otherroles.sort(key=lambda x : x.contributor.name)

        return self.project == other.project and str(roles) == str(otherroles)

    def add_contrib(self, skill: Skill, contrib: Contributor):
        role = Role(skill, contrib)
        self.roles.append(role)

    def get_must_mentor_roles(self):
        roles = []

        for role in self.roles:
            if role.need_mentoring():
                roles.append(role)

        return roles

    def get_mentor_for_role(self, role2: Role) -> Contributor:
        for role in self.roles:
            if role == role2:
                continue

            if role.contributor.has_skill(role.skill, mentoringAvailable=False):
                return role.contributor

        return None

    def get_open_skills(self) -> List[Skill]:
        open_skills = []

        for skill in self.project.neededSkills:
            found = False

            for role in self.roles:
                if role.skill == skill:
                    found = True
                    break
            
            if found:
                continue

            open_skills.append(skill)

        return open_skills

    def get_metrics(self):
        count: int = 0
        max_val: int = 0

        for role in self.roles:
            contributor_skill = role.contributor.get_skill(role.skill.type)
            if role.skill.level == contributor_skill.level or role.skill.level - 1 == contributor_skill.level:
                count += 1
                max_val = max(max_val, contributor_skill.level)

        return count, max_val

    def fitness(self, currentDay: int) -> int:
        count, max = self.get_metrics()
        score: int = count * 1000
        score += self.project.worth(currentDay) * 100
        score += max * 10

        return score

    def can_start_with(self, contribs: List[Contributor]) -> bool:
        for role in self.roles:
            if role.contributor not in contribs:
                return False

        return True


def get_available_contributors(contribs: List[Contributor], skillReq: Skill=None, mentoringAvailable=False):
    if skillReq is None:
        temp = []

        for contrib in contribs:
            if not contrib.has_project():
                temp.append(contrib)

        return temp
    else:
        temp = []

        for contrib in contribs:
            if not contrib.has_project() and contrib.has_skill(skillReq, mentoringAvailable):
                temp.append(contrib)

        return temp


def get_available_projects(projects: List[Project], contribs: List[Contributor]) -> List[Project]:
    avail_projects = []

    for project in projects:
        if not project.is_open():
            continue
        
        shitty = False

        for skill in project.neededSkills:
            if len(get_available_contributors(contribs, skill)) == 0:
                shitty = True
                break

        if shitty:
            continue

        avail_projects.append(project)

    return avail_projects


def get_current_projects(projects: List[Project]) -> List[Project]:
    res: List[Project] = []

    for project in projects:
        if project.is_in_progress():
            res.append(project)

    return res


def get_skillup_contributors_for_project(rolecomp: RoleComposition, contribs: List[Contributor]):
    skillup_contribs = []

    
    for skill in rolecomp.project.neededSkills:
        for contrib in contribs:
            if contrib.has_skill_up(skill):
                skillup_contribs.append(contrib)

    return skillup_contribs


def calc_role_compositions(project: Project, contribs: List[Contributor]) -> List[RoleComposition]:
    rolecomps: List[RoleComposition] = []
    
    for skill in project.neededSkills:
        for contrib in contribs:
            if contrib.has_skill(skill, mentoringAvailable=True):
                rolecomp = RoleComposition(project)
                rolecomp.add_contrib(skill, contrib)

                rolecomps.append(rolecomp)
    
    for rolecomp in rolecomps:
        for skill in rolecomp.get_open_skills():
            for contrib in contribs:
                if contrib.has_skill(skill, mentoringAvailable=True):
                    rolecomp.add_contrib(skill, contrib)

    res: List[RoleComposition] = []

    for rolecomp in rolecomps:
        for role in rolecomp.roles:
            if role.needs_mentoring() and rolecomp.get_mentor_for_role(role) is not None:
                res.append(rolecomp)

    res2: List[RoleComposition] = []

    for rolecomp in rolecomps:
        dupl = False

        for role in rolecomp.roles:
            for role2 in rolecomp.roles:
                if role != role2 and role.contributor == role2.contributor:
                    dupl = True
                    break

        if not dupl:
            res2.append(rolecomp)         

    result: List[RoleComposition] = []

    for rolecomp in res2:
        if rolecomp not in result:
            result.append(rolecomp)
            #print(rolecomp)

    return result


def main():
    lines = []
    #for fp in ['.\\OnlineQ\\input\\a_an_example.in.txt']:
    for fp in ['.\\OnlineQ\\input\\b_better_start_small.in.txt']:

        start = time.time()
        with open(fp) as f:
            print('Calculating best solution:' + fp + "!")
            lines = f.readlines()

        split0 = lines[0].split(' ')

        cont_count = int(split0[0])
        proj_count= int(split0[1])

        contribs: List[Contributor] = []
        pos:int = 1

        for i in range(0, cont_count):
            currcont = Contributor(lines[pos])
            currcont.skills = []

            pos += 1

            for j in range(0, currcont.skillcount):
                currcont.skills.append(Skill(lines[pos+j]))

            pos += currcont.skillcount
            contribs.append(currcont)

        projects = []

        for j in range(0, proj_count):
            currproj = Project(lines[pos])
            currproj.neededSkills = []

            pos += 1

            for k in range(0, currproj.skillcount):
                currproj.neededSkills.append(Skill(lines[pos+k]))

            pos += currproj.skillcount

            projects.append(currproj)

        currentDay = 0
        asd = 0
        while True:
            compositions = []
            current_projects = get_current_projects(projects)

            avail_projects = get_available_projects(projects, contribs)

            if len(avail_projects) == 0 and len(current_projects) == 0:
                break

            avail_contribs: List[Contributor] = []

            for contrib in contribs:
                if not contrib.has_project():
                    avail_contribs.append(contrib)

            for project in avail_projects:
                compositions.append((project, calc_role_compositions(project, avail_contribs)))

            for p, comps in compositions:
                project: Project = p
                compslist:List[RoleComposition] = comps
                compslist.sort(key=lambda c: c.fitness(currentDay))

                for comp in compslist:
                    if comp.can_start_with(avail_contribs):
                        project.start(comp.roles)
                        asd += 1
                        print("Starting " + str(project))

                        current_projects.append(project)

                        for role in comp.roles:
                            avail_contribs.remove(role.contributor)

            for project in current_projects:
                project.progress(1)
                if project.status == PROJECT_DONE:
                    asd -= 1

            print("Current: " + str(asd))
            currentDay += 1
            if currentDay > 300:
                break
    
        with open(fp + ".output", "w+") as fo:
            fo.write(str(len(schedule)) + "\n")
            for timing in schedule:
                fo.write(timing.projectname + "\n")
                first = True
                for worker in timing.workers:
                    fo.write( worker)
                    if not first:
                        fo.write(" ")
                    first = False

                fo.write("\n")
     

def dump_outfile(rules, infilename):
    with open(infilename[:-3] + ".out", "w") as outf:
        outf.write(str(len(rules))  + "\n")
        for rule in rules:
            rules[rule].serialize(outf)
    print('Output written...')
    

if __name__ == "__main__":
    main()

