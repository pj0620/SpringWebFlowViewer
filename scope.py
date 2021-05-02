class Context:
    def __init__(self, track_vars):
        self.vars = {var: ScopeVariable(var, None) for var in track_vars}
        self.varsNameSet = set(track_vars)

    def containsVar(self, varName):
        return varName in self.varsNameSet

    def getVar(self, varName):
        return self.vars[varName]

    def __str__(self):
        res = ""
        for var in self.vars.values():
            res += var.name + "=" + str(var.vals) + ","
        if len(res) > 0:
            return res[:-1]
        else:
            return ""


class ScopeVariable:
    def __init__(self, name, vals):
        self.name = name
        self.vals = vals

    def set_vals(self, new_vals):
        self.vals = new_vals

        for i in range(len(self.vals)):
            if self.vals[i][0] == "'":
                self.vals[i] = self.vals[i][1:]
            if self.vals[i][-1] == "'":
                self.vals[i] = self.vals[i][:-1]

    def get_vals(self):
        return self.vals