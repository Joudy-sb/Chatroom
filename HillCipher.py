import numpy as np 
class EncryptHC:
    # global variable storing the alphabet
    alphabet = [chr(i) for i in range(97, 123)]
    def __init__(self,message, key, mod):
        self.message = message
        self.key = key
        self.mod = mod
        
    #THIS FUNCTION COMPUTES THE MATRIX MULTIPLICATION
    def matrix_mult_HC(self,plaintext_int, key,mod):
        ciphertext_int=[]
        for i in range(len(key)):
            char_enc=0
            for j in range(len(plaintext_int)):
                char_enc += (key[i][j]*plaintext_int[j])
            ciphertext_int.append(char_enc%mod)
        return ciphertext_int

    #THIS FUNCTION REMOVES AND PRESERVE SPECIAL CHARACTERS
    def preserve_special_char(self,plaintext):
        special_char = []
        preserved_text = ""
        for i in range(0,len(plaintext)):
            if plaintext[i].isalpha()!=True:
                special_char.append((plaintext[i],i))
            else:
                preserved_text += plaintext[i]
        return (preserved_text, special_char)

    #THIS FUNCTION ADD BACK THE SPECIAL CHARACTERS
    def add_preserved_special_char(self,ciphertext, special_char):
        ciphertext = list(ciphertext)
        for i in special_char: 
            ciphertext.insert(i[1],i[0])
        return ''.join(ciphertext)

    #FUNCTION THAT FINDS THE MODULAR INVERSE
    def mod_inv(self,a, m):
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"{a} has no inverse mod {m}")

    #FUNCTION THAT CHECKS IF A MATRIX IS INVERTIBLE
    def matrix_mod_inv(self,matrix, mod):
        matrix = np.array(matrix, dtype=int)
        det = int(round(np.linalg.det(matrix))) % mod
        if det == 0:
            raise ValueError(f"{matrix} has a determinant of 0 and therefor is not inversible.")
        det_inv = self.mod_inv(det, mod)
        adj = self.matrix_cofactor(matrix).T
        matrix_inv = np.mod(det_inv * adj, mod)
        return matrix_inv

    #THIS FUNCTION WILL ENCRYPT/DECRYPT A TEXT USING A KEY/INVERSE KEY
    def HillCipher(self,plaintext: str, key: list[list[int]], mod: int) -> str:
        #check if key is invertible, i.e. if the determinant of the matrix is not 0
        self.matrix_mod_inv(key, mod)
        preserved_text, special_char = self.preserve_special_char(plaintext)
        #check if the string is compatible with key
        if len(preserved_text)%len(key)!=0:
            preserved_text+=(len(key)-len(preserved_text)%len(key))*"x"
        ciphertext=[]
        # for every k character in the plain text, k being the size of the matrix
        for i in range (0,len(preserved_text),len(key)):
            plaintext_int = []
            for j in range (i,i+len(key)):
                plaintext_int.append(self.alphabet.index(preserved_text[j].lower()))
            ciphertext_int = []
            ciphertext_int = self.matrix_mult_HC(plaintext_int, key,mod) 
            for j in range (len(ciphertext_int)):
                ciphertext.append(self.alphabet[ciphertext_int[j]])
        ciphertext = self.add_preserved_special_char(ciphertext,special_char)
        return ''.join(ciphertext)

    #THIS FUNCTION FINDS THE COFACTOR MATRIX TO FIND THE INVERSE
    def matrix_cofactor(self,matrix):
        nrows, ncols = matrix.shape
        cofactor_matrix = np.zeros((nrows, ncols), dtype=int)
        for i in range(nrows):
            for j in range(ncols):
                minor = np.delete(matrix, i, 0)
                minor = np.delete(minor, j, 1)
                cofactor_matrix[i, j] = ((-1) ** (i + j)) * int(round(np.linalg.det(minor)))
        return cofactor_matrix

    # Function that encrypts a text
    def encrypt(self, plaintext: str) -> str:
        return self.HillCipher(plaintext, self.key, self.mod)

    # Function that decrypts a text
    def decrypt(self, ciphertext: str) -> str:
        inverse_key = self.matrix_mod_inv(self.key, self.mod)
        return self.HillCipher(ciphertext, inverse_key, self.mod)

'''
def main():
    # Define the key matrix (must be invertible mod 26)
    key_matrix = [[7, 1], [2, 5]]

    # Define the message to encrypt
    message = "this i@#s a secr!et meW$ssage"

    # Define the modulus (for English alphabet, it's usually 26)
    mod = 26

    # Create an instance of EncryptHC
    cipher = EncryptHC(message, key_matrix, mod)

    # Encrypt the message
    encrypted_message = cipher.encrypt(message)
    print(f"Encrypted Message: {encrypted_message}")

    # Decrypt the message
    decrypted_message = cipher.decrypt(encrypted_message)
    print(f"Decrypted Message: {decrypted_message}")

    # Check if the decryption matches the original message
    if decrypted_message.replace('x', '') == message:
        print("Success! The decrypted message matches the original.")
    else:
        print("Something went wrong, the decrypted message does not match the original.")

if __name__ == "__main__":
    main()
'''