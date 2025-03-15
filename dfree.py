def generate_wav_sequence(number):
    """
    Generates the sequence of .wav files for a given number, strictly following the pattern:
    - For numbers like 1001: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"]
    - For numbers like 2001: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"]
    - For numbers like 10001: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"]
    """
    # Base wav files for numbers
    base_wavs = {
        0: "0.wav",
        1: "1.wav",
        2: "2.wav",
        3: "3.wav",
        4: "4.wav",
        5: "5.wav",
        6: "6.wav",
        7: "7.wav",
        8: "8.wav",
        9: "9.wav",
        10: "10.wav",
        20: "20-90.wav",
        30: "20-90.wav",
        40: "20-90.wav",
        50: "20-90.wav",
        60: "20-90.wav",
        70: "20-90.wav",
        80: "20-90.wav",
        90: "20-90.wav",
        100: "100.wav",
        1000: "1000.wav",
        10000: "10000.wav",
        100000: "100000.wav",
        1000000: "1000000.wav",
    }

    # Special wav files
    ke_wav = "KƐ.wav"
    nya_wav = "NYÃ.wav"

    # Check if the number is in the master_code
    if number in master_code:
        return master_code[number]

    # Handle numbers less than 100
    if number < 100:
        if number in base_wavs:
            return [base_wavs[number]]
        elif 11 <= number < 20:
            return [base_wavs[10], ke_wav, base_wavs[number % 10]]
        else:
            tens = (number // 10) * 10
            units = number % 10
            return [base_wavs[tens], ke_wav, base_wavs[units]]

    # Handle numbers in the hundreds
    if 100 <= number < 1000:
        hundreds = number // 100
        remainder = number % 100
        if remainder == 0:
            return [base_wavs[100], base_wavs[hundreds]]
        else:
            return [base_wavs[100], base_wavs[hundreds]] + generate_wav_sequence(remainder)

    # Handle numbers in the thousands (strictly following the pattern)
    if 1000 <= number < 10000:
        thousands = number // 1000
        remainder = number % 1000
        if remainder == 0:
            return [base_wavs[1000], base_wavs[thousands]]
        else:
            return [base_wavs[1000], base_wavs[thousands], ke_wav, nya_wav] + generate_wav_sequence(remainder)

    # Handle numbers in the ten-thousands (strictly following the pattern)
    if 10000 <= number < 100000:
        ten_thousands = number // 10000
        remainder = number % 10000
        if remainder == 0:
            return [base_wavs[10000], base_wavs[ten_thousands]]
        else:
            return [base_wavs[10000], base_wavs[ten_thousands], ke_wav, nya_wav] + generate_wav_sequence(remainder)

    # Handle numbers in the hundred-thousands (strictly following the pattern)
    if 100000 <= number < 1000000:
        hundred_thousands = number // 100000
        remainder = number % 100000
        if remainder == 0:
            return [base_wavs[100000], base_wavs[hundred_thousands]]
        else:
            return [base_wavs[100000], base_wavs[hundred_thousands], ke_wav, nya_wav] + generate_wav_sequence(remainder)

    # Handle numbers in the millions (strictly following the pattern)
    if 1000000 <= number < 10000000:
        millions = number // 1000000
        remainder = number % 1000000
        if remainder == 0:
            return [base_wavs[1000000], base_wavs[millions]]
        else:
            return [base_wavs[1000000], base_wavs[millions], ke_wav, nya_wav] + generate_wav_sequence(remainder)

    # Handle larger numbers (billions, trillions, etc.)
    if number >= 10000000:
        magnitude = 1000000  # Start with millions
        while number // magnitude == 0:
            magnitude *= 1000
        main_part = number // magnitude
        remainder = number % magnitude
        if remainder == 0:
            return [base_wavs[magnitude], base_wavs[main_part]]
        else:
            return [base_wavs[magnitude], base_wavs[main_part], ke_wav, nya_wav] + generate_wav_sequence(remainder)

    return []