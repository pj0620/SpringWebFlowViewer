class Context:
    def __init__(self, track_vars):
        self.vars = {var: ScopeVariable(var, None) for var in track_vars}
        self.varsNameSet = set(track_vars)

    def containsVar(self, varName):
        return varName in self.varsNameSet

    def getVar(self, varName):
        return self.vars[varName]

class ScopeVariable:
    def __init__(self, name, vals):
        self.name = name
        self.vals = vals
