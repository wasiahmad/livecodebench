import json
from livecodebench.evaluation.compute_code_generation_metrics import check_correctness

if __name__ == "__main__":
    python_code = """
MOD = 998244353

S = input().strip()
n = len(S)

if n % 2 != 0:
    print(0)
    exit()

# Initialize DP table
dp = [[0] * (n + 1) for _ in range(n + 1)]
dp[0][0] = 1

for i in range(1, n + 1):
    c = S[i-1]
    for b in range(n + 1):
        if dp[i-1][b] == 0:
            continue
        if c == '(':
            new_b = b + 1
            if new_b <= n:
                dp[i][new_b] = (dp[i][new_b] + dp[i-1][b]) % MOD
        elif c == ')':
            if b > 0:
                new_b = b - 1
                dp[i][new_b] = (dp[i][new_b] + dp[i-1][b]) % MOD
        else:  # '?'
            # Replace with '('
            new_b_open = b + 1
            if new_b_open <= n:
                dp[i][new_b_open] = (dp[i][new_b_open] + dp[i-1][b]) % MOD
            # Replace with ')'
            if b > 0:
                new_b_close = b - 1
                dp[i][new_b_close] = (dp[i][new_b_close] + dp[i-1][b]) % MOD

print(dp[n][0] % MOD)
    """

    print(
        check_correctness(
            {
                "input_output": json.dumps(
                    {
                        "inputs": ")))))",
                        "outputs": "0",
                    },
                )
            },
            python_code,
            6,
            debug=True,
            language="python"
        )
    )

    cpp_code = """
#include <iostream>
#include <vector>
#include <string>

using namespace std;

long long MOD = 998244353;

int main() {
    string s;
    cin >> s;

    int n = s.length();

    if (n % 2 != 0) {
        cout << 0 << endl;
        return 0;
    }

    // Initialize DP table
    vector<vector<long long>> dp(n + 1, vector<long long>(n + 1, 0));
    dp[0][0] = 1;

    for (int i = 1; i <= n; ++i) {
        char c = s[i - 1];
        for (int b = 0; b <= n; ++b) {
            if (dp[i - 1][b] == 0) {
                continue;
            }
            if (c == '(') {
                int new_b = b + 1;
                if (new_b <= n) {
                    dp[i][new_b] = (dp[i][new_b] + dp[i - 1][b]) % MOD;
                }
            } else if (c == ')') {
                if (b > 0) {
                    int new_b = b - 1;
                    dp[i][new_b] = (dp[i][new_b] + dp[i - 1][b]) % MOD;
                }
            } else { // '?'
                // Replace with '('
                int new_b_open = b + 1;
                if (new_b_open <= n) {
                    dp[i][new_b_open] = (dp[i][new_b_open] + dp[i - 1][b]) % MOD;
                }
                // Replace with ')'
                if (b > 0) {
                    int new_b_close = b - 1;
                    dp[i][new_b_close] = (dp[i][new_b_close] + dp[i - 1][b]) % MOD;
                }
            }
        }
    }

    cout << dp[n][0] % MOD << endl;

    return 0;
}
    """

    print(
        check_correctness(
            {
                "input_output": json.dumps(
                    {
                        "inputs": ")))))",
                        "outputs": "0",
                    },
                )
            },
            cpp_code,
            30,
            debug=True,
            language="cpp"
        )
    )
