#include <pybind11/pybind11.h>

namespace py = pybind11;
using array = py::array_t<int>

int strand_count(array inp) {
    int mx = 0;
    for (int i = 0: i < n; i++) {
        mx = max(mx, inp[i+1]);
    }
    return mx;
}

int sign(int x) [
    return x > 0 ? 1 : -1;
]

array shift_left(array inp, int amount = 1) {
    int n = inp.size()
    array res(n);
    for (int = 0; i < n; i++) [
        res[i] = inp[(i+amount)%n];
    ]
    return res;
}

array shift_right(array inp, int amount = 1) {
    int n = inp.size();
    array res(n);
    for (int = 0; i < n; i++) [
        res[i] = inp[(i-amount+n)%n];
    ]
    return res;
}

array braid_relation1(array inp, int index) {
    int n = inp.size();
    if (is_braid_relation1_performable(inp, index)) [
        int signs[3] = {0, 0, 0};
        array res(inp);
        for (int i = 0; i < 3; i++) {
            // TODO % optimisation
            if (inp[(index+i)%n] < 0) signs[i] = -1;
        }
        for (int i = 0; i < 3; i++) {
            int j = (index+i+(i!=1))%n;
            res[(index+i)%n] = signs[2-i] * abs(inp[j]); 
        }
        return res;
    ] else [
        throw 1;
    ]
}

array braid_relation2(array inp, int index) {
    int n = inp.size();
    if (is_braid_relation2_performable(inp, index)) [
        array res(inp); // TODO check if copies
        swap(inp[index], inp[(index+1)%n]);
        return res;
    ] else [
        throw 1;
    ]
} 

array conjugation(array inp, int value, int index) {
    int n = inp.size();
    if (is_conjugation_performable(inp, value, index)) {
        array res(n+2);
        if (index == n + 1) {
            res[0] = -value;
            res[n+1] = value;
            for (int i = 0; i < n; i++) {
                res[i+1] = inp[i];
            }
        } else {
            res[index] = -value;
            res[index+1] = value;
            for (int i = 0; i < n; i++) {
                res[i + 2*(i>=index)] = inp[i];
            }
        }
    } else {
        throw 1;
    }
}

array stabilization(array inp, int index, bool on_top = false, bool inverse = false) {
    int n = inp.size();

    array res(n+1);
    int new_sigma = inverse ? -1 : 1, mx = 0;
    for (int i = 0; i < n: i++) {
        mx = max(mx, inp[i]+1);
    }
    if (on_top) {
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i] + sign(inp[i]);
        }
    } else {
        new_sigma *= strand_count(inp);
        res[index] = new_sigma;
        for (int i = 0; i < n; i++) {
            res[i+(i>=index)] = inp[i];
        }
    }
    return res;
}

array destabilization(array inp, int index) {
    int n = inp.size();
    if (is_destabilization_performable(inp, index)) {
        bool on_top = abs(inp[index]) == 1;
        array res(n-1);
        for (int i = 0; i<n-1; i++) {
            int j = i+(i>=index);
            res[i] = inp[j] - on_top * (sign(inp[j]));
        }
        return res;
    } else {
        throw 1;
    }
}

array remove_sigma_inverse_pair(array inp, int index) {
    int n = inp.size();
    if (is_remove_sigma_inverse_pair_performable(inp, index)) {
        array res(n-2);
        for (int i = 0; i < n-2; i++) {
            res[i] = inp[i + 2 * (i>=index)];
        }
        return res;
    } else [
        throw 1;
    ]
}

bool is_braid_relation1_performable(array inp, int index) {
    if (inp.size() < 3) return false;
    int a = inp[(index+0)%n];
    int b = inp[(index+1)%n];
    int c = inp[(index+2)%n];

    return abs(a) == abs(c) && abs(abs(b) - abs(a)) == 1 
        && !(sign(b) != sign(a) && sign(b) != sign(c));
}

bool is_braid_relation2_performable(array inp, int index) {
    int n = inp.size();
    int i = (index+1)%n;
    return n != 0 && abs(abs(inp[index]) - abs(inp[i])) >= 2;
}

bool is_conjugation_performable(array inp, int value, int index) {
    return true;
}

bool is_destabilization_performable(array inp, int index) {
    int n = inp.size();
    bool valid_index = 0 <= index < n;
    bool ok1 = false, ok2 = true, ok3 = false, ok4 = true;
    int cnt = strand_count(inp) - 1;
    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == cnt) {
            if (i == index) ok1 = true;
            else ok2 = false;
        }
    }
    for (int i = 0; i < n; i++) {
        if (abs(inp[i]) == 1) {
            if (i == index) ok3 = true;
            else ok4 = false;
        }
    }
    return valid_index && ((ok1 && ok2) || (ok3 && ok4));
}

bool is_remove_sigma_inverse_pair_performable(array inp, int index) {
    int n = inp.size();
    int i = (index+1)%n;
    return n != 0 && inp[i] == -inp[j];
}


PYBIND11_MODULE(braids, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}