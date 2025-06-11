# Differential Fault Analysis on DES: Fault Injection on Round 15 Output (R15)
This project presents a Differential Fault Analysis (DFA) attack targeting the Data Encryption Standard (DES) algorithm by injecting faults at the output of the 15th round, specifically on the right half of the data block (R15). This method enables an attacker to retrieve the secret encryption key with significantly fewer computations than a brute-force attack, which would require testing all 2⁵⁶ possible keys.
# Attack Context
The attack assumes that the adversary has physical access to the device executing DES, such as a smart card, and the ability to inject controlled faults. These faults are introduced during the encryption process, targeting only the output of the 15th round, denoted as R15. Faults can be caused using methods like clock glitches, voltage fluctuations, or laser beams.

Additionally, it is assumed that the attacker operates in a chosen plaintext scenario, meaning they can choose the plaintext to be encrypted and obtain both the correct ciphertext (without fault) and the faulty ciphertext (with fault injected at R15). The attacker also has complete knowledge of the DES algorithm, including its internal components (S-boxes, permutations, and key schedule).
# Structure of DES and Role of R15
DES is a 16-round block cipher that operates on 64-bit blocks and uses a 56-bit key (with 8 parity bits for a total of 64 bits). It follows a Feistel network structure where each round applies the function:
Lᵢ = Rᵢ₋₁  
Rᵢ = Lᵢ₋₁ ⊕ f(Rᵢ₋₁, Kᵢ)
The function f(R, K) expands R to 48 bits, XORs it with the round key K, passes it through 8 S-boxes (each outputting 4 bits), and permutes the result using the P permutation. The output of the final round is (L16, R16), which is reversed and passed through the final permutation (IP⁻¹) to produce the ciphertext.

By targeting R15, the attacker interferes with the input to the 16th round, making it possible to isolate the effect of the fault in that final round and exploit it.

# Fault Injection and Observed Difference
When no fault is injected, the 16th round behaves normally:
L16 = R15  
R16 = L15 ⊕ f(R15, K16)
With a fault injected at R15 (let's denote the faulty version as R15*), the output becomes:
L16* = R15*  
R16* = L15 ⊕ f(R15*, K16)
Since L15 remains unchanged, the difference observed between the correct and faulty ciphertexts is due solely to the difference in f(R15, K16) and f(R15*, K16). This gives:
ΔR16 = R16 ⊕ R16* = f(R15, K16) ⊕ f(R15*, K16)
To analyze this, the attacker reverses the final permutation:
ΔRout = P⁻¹(ΔR16) = output_difference_of_f
This difference corresponds to differences at the output of the S-boxes in the final round.
# Exploiting S-boxes to Recover Key Bits
The function f(R, K) involves 8 S-boxes, each taking a 6-bit input and producing a 4-bit output. These S-boxes are the only nonlinear components of DES, making them a key target in the analysis.

For each S-box S_j, the attacker analyzes:
ΔS_j = S_j(E(R15)_j ⊕ K16_j) ⊕ S_j(E(R15*)_j ⊕ K16_j)
Where:

E(R15)_j is the 6-bit input to S-box j after expansion.

K16_j is the 6-bit part of the round key K16 used in S-box j.

By trying all 64 possible values of K16_j and comparing the resulting differences against the observed ΔS_j, the attacker can find candidate key values for each S-box that explain the fault.

A single faulty ciphertext usually results in several possible candidates per S-box, but repeating the attack with different injected faults significantly narrows down the candidate set. In practice, using around 32 different faulty ciphertexts is enough to determine the correct 6-bit key for each S-box, reconstructing the full 48-bit subkey K16.
# Recovering the Full DES Key from K16
DES generates subkeys from the main 56-bit key using a fixed key schedule:

The 64-bit key (with 8 parity bits) is reduced to 56 bits via PC-1.

Then, for each round, the key bits are shifted and compressed to 48 bits via PC-2 to produce the subkey.

Since PC-2 drops 8 bits from the 56-bit key, even if we perfectly recover K16, there is some ambiguity. Specifically, we must brute-force the 8 missing bits, which correspond to the following key positions:9, 18, 22, 25, 35, 38, 43, 54
This is a feasible brute-force task (only 2⁸ = 256 possibilities). For each candidate:

Reconstruct the full 56-bit key.

Generate the DES key schedule and check whether it produces the known K16.

Use the key to encrypt the original plaintext.

If the resulting ciphertext matches the correct one, the key is found.
# Conclusion
This Differential Fault Analysis attack demonstrates the practical vulnerability of DES when fault injection is possible. It highlights that a single well-placed fault, combined with mathematical analysis of the internal round structure and S-box behavior, can dramatically reduce the key search space.

The approach used here is not specific to DES and can inspire similar attacks on other block ciphers—especially those with Feistel structures or fixed S-boxes. The main takeaway is that fault injection is a powerful cryptanalytic technique and must be considered when designing secure hardware implementations.

