class Context:
    def __init__(self, track_vars):
        self.vars = {var: frozenset() for var in track_vars}
        self.hash = 0
        self.compute_hash()

    def contains_var(self, var_name):
        return var_name in self.vars.keys()

    def get_vals(self, var_name):
        return self.vars[var_name]

    def set_var(self, var_name, new_vals):
        for i in range(len(new_vals)):
            if new_vals[i][0] == "'":
                new_vals[i] = new_vals[i][1:]
            if new_vals[i][-1] == "'":
                new_vals[i] = new_vals[i][:-1]

        self.vars[var_name] = frozenset(new_vals)

        # update hash of context
        self.compute_hash()

    def compute_hash(self):
        vars_frozen = frozenset((var_name, vals) for var_name, vals in self.vars.items())
        self.hash = hash(vars_frozen)

    def __hash__(self):
        return self.hash

    def __str__(self):
        res = ""
        for var_name, vals in self.vars.items():
            res += var_name + "=" + str(vals) + ","
        if len(res) > 0:
            return res[:-1]
        else:
            return ""

    def __eq__(self, other):
        return self.vars == other.vars

    def __ne__(self, other):
        return not (self == other)