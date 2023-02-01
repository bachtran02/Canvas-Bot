def makeBold(string: str):
    return f"**{string}**"

def makeLink(string: str, link: str):
    return f"[{string}]({link})"

def buildDeadlineChoices(courses: dict):
    command_choices = []

    for course in courses:
        command_choices.append(f"{course['id']} - {course['name']}")
    return command_choices
    
def toPercent(value: float, base: float):
    return round(value/float(base) * 100, 2)

def shortenCrnName(name: str):
    return " ".join(name.split(" ", 3)[:3])