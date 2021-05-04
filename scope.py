class Context:
    def __init__(self, track_vars):
        self.vars = {var: frozenset() for var in track_vars}
        self.changed_vars = set()
        self.hash = 0

    def contains_var(self, var_name):
        return var_name in self.vars.keys()

    def get_vals(self, var_name):
        return self.vars[var_name]

    def set_var(self, var_name, new_vals):
        if not new_vals:
            raise Exception("scope variables cannot be set to empty set after initialization, messes up hashing")

        for i in range(len(new_vals)):
            if new_vals[i][0] == "'":
                new_vals[i] = new_vals[i][1:]
            if new_vals[i][-1] == "'":
                new_vals[i] = new_vals[i][:-1]

        old_vals = self.vars[var_name]
        self.vars[var_name] = frozenset(new_vals)

        # update hash of context
        update_changes = False
        if var_name not in self.changed_vars:
            update_changes = True
            self.changed_vars.add(var_name)
        update_changes = update_changes or old_vals != new_vals
        if update_changes:
            changed_set = frozenset((var_name, self.vars[var_name]) for var_name in self.changed_vars)
            self.hash = hash(changed_set)

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