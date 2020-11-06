def getGradeSymbol(gradeNumber):
    '''
    Grade numbers in aquarius correspond to specific conditions, decode and assign letter grade
    '''
    if gradeNumber == "10":  # ICE
        symbol = "B"
    elif gradeNumber == "20":  # ESTIMATED
        symbol = "E"
    elif gradeNumber == "30":  # PARTIAL
        symbol = "A"
    elif gradeNumber == "40":  # DRY
        symbol = "D"
    else:
        symbol = "None"
    return symbol