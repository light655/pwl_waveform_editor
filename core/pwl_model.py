def sciparse(sci_str):
    sci_dict = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, '%': 1e-2, 'k': 1e3, 'M': 1e6, 'G': 1e9}
    try:
        sci_str = str(sci_str).strip()
        if not sci_str:
            raise ValueError("Empty input string")
        if sci_str[-1].isdecimal():
            val = float(sci_str)
        else:
            val = float(sci_str[:-1])
            val *= sci_dict[sci_str[-1]]

        return val
    except (ValueError, KeyError, IndexError) as err:
        raise ValueError(f"Invalid value: '{sci_str}'") from err


def sciprint(val):
    if val == 0:
        return "0"
    elif val < 1e-9:
        return f"{val*1e12:.3f}p"
    elif val < 1e-6:
        return f"{val*1e9:.3f}n"
    elif val < 1e-3:
        return f"{val*1e6:.3f}u"
    elif val < 1:
        return f"{val*1e3:.3f}m"
    elif val < 1e3:
        return f"{val:.3f}"
    elif val < 1e6:
        return f"{val/1e3:.3f}k"
    else:
        return f"{val/1e6:.3f}M"

class PWLWaveform:
    def __init__(self):
        # Initialize points for the piecewise linear waveform
        self.node_x = [0.0]
        self.node_y = [0.0]

    def add_point(self, x, y):
        """Add a new point to the waveform."""

        # Avoid adding duplicated x-values
        if len(self.node_x) > 1:
            x_range = self.node_x[-1] - self.node_x[0]

            for existing_x in self.node_x:
                if abs(existing_x - x) < (1e-6 * x_range):
                    print(f"Point at x={x} already exists. Skipping addition.")
                    return

        # Inserting the point at the correct position to maintain sorted order
        if len(self.node_x) == 0 or x < self.node_x[0]:
            self.node_x.insert(0, x)
            self.node_y.insert(0, y)
        elif x > self.node_x[-1]:
            self.node_x.append(x)
            self.node_y.append(y)
        else:
            for i in range(len(self.node_x) - 1):
                if self.node_x[i] < x < self.node_x[i + 1]:
                    self.node_x.insert(i + 1, x)
                    self.node_y.insert(i + 1, y)
                    break

    def update_point_position(self, index, new_x, new_y):
        if 0 <= index < len(self.node_x):
            self.node_x[index] = new_x
            self.node_y[index] = new_y
            pairs = sorted(zip(self.node_x, self.node_y))
            self.node_x = [p[0] for p in pairs]
            self.node_y = [p[1] for p in pairs]

    def remove_point(self, index):
        if 0 <= index < len(self.node_x):
            self.node_x.pop(index)
            self.node_y.pop(index)