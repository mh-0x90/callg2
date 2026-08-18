from olten3_3 import adad

def checkit(value: str) -> str:
    if adad(value) == True:
        return "*****"
    else:
        return value.lower()
    
