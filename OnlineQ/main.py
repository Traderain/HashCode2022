import io, math
from visualise_graph import Graph, dijsktra
import time


car_count = 1
simlen = 1

class Contributor:
    name = ""
    skillcount = 0
    skills = []
    def __init__(self, line):
        splt = line.split(' ')
        self.name = splt[0]
        self.skillcount = int(splt[1].strip())

class Skill:
    type = ""
    level = 1
    def __init__(self, line):
        splt = line.split(' ')
        self.type = splt[0]
        self.level = int(splt[1].strip())


class Project:
    name = ""
    duration = 0
    score = 0
    best_before = 0
    skillcount = 0
    neededskills = []

    def __init__(self, line):
        splt = line.split(' ')
        self.name = splt[0]
        self.duration = int(splt[1].strip())
        self.score = int(splt[2].strip())
        self.best_before = int(splt[3].strip())
        self.skillcount = int(splt[4].strip())
        


def main():
    lines = []
    for fp in ['.\\OnlineQ\\input\\a_an_example.in.txt']:

        start = time.time()
        with open(fp) as f:
            print('Calculating best solution:' + fp + "!")
            lines = f.readlines()

        split0 = lines[0].split(' ')

        cont_count = int(split0[0])
        proj_count= int(split0[1])

        contribs = []
        pos = 1

        for i in range(0, cont_count):
            currcont = Contributor(lines[pos])
            currcont.skills = []

            pos += 1

            for j in range(0, currcont.skillcount):
                currcont.skills.append(Skill(lines[pos+j]))

            pos += currcont.skillcount
            contribs.append(currcont)

        print("Contributors:")

        for c in contribs:
            print("\t" + c.name)
            for s in c.skills:
                print("\t\t" + s.type + " " + str(s.level))

        projects = []

        for j in range(0, proj_count):
            currproj = Project(lines[pos])
            currproj.neededskills = []

            pos += 1

            for k in range(0, currproj.skillcount):
                pskill = Skill(lines[pos+k])

            pos += currproj.skillcount

            projects.append(currproj)

        print("Projects:")

        for project in projects:
            print("\t" + project.name)
            for skill in project.neededskills:
                print("\t\t" + skill.type + " " + str(skill.level))

        
        
def dump_outfile(rules, infilename):
    with open(infilename[:-3] + ".out", "w") as outf:
        outf.write(str(len(rules))  + "\n")
        for rule in rules:
            rules[rule].serialize(outf)
    print('Output written...')
    

if __name__ == "__main__":
    main()

