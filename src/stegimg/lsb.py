import sys
import os.path
from PIL import Image

#######################
# Helper Functions  ##
#######################


def string_to_bits(string):
    """
    Convert a string to its bit representation.
    """
    bits = ""
    for letter in string:
        letter_byte = ord(letter)
        # This ensures the bit representation of each letter is padded with
        # zeros to length 8
        bits += format(letter_byte, "08b")
    return bits


def bits_to_string(bits):
    """
    Convert a bit string to an ASCII string.
    """
    string = ""
    # Step through the bits one byte at a time
    for start in range(0, len(bits), 8):
        byte = bits[start:start+8]
        string += chr(int(byte, 2))
    return string


def replace_lsb(bits, replacement_bit):
    """
    Replace the least significant bit.
    """
    # Replace the least significant bit with zero
    lsb_zero = bits & (~1)
    # With the least significant bit equal to 0, a bitwise OR with the
    # replacement bit ensures the lsb is equal to the replacement bit
    return lsb_zero | replacement_bit


def recover_lsb(bits):
    """
    Extract the least significant bit.
    """
    lsb = bits & 1
    return lsb


def file_from_user(input_message, bundle_dir):
    """
    Get a valid file from user input. The file must be in the same directory
    as the application.
    """
    file_path = ""
    valid_file = False
    while not valid_file:
        file_name = input(input_message)
        file_path = os.path.join(bundle_dir, file_name)
        valid_file = os.path.isfile(file_path)
        if not valid_file:
            print(f"{file_path} is not a valid file.")
    return file_path


def get_user_choice(message, options):
    """
    Get user to choose from a range of options. User input is sanitised and
    checked to ensure it is valid.
    """
    valid_choice = False
    while not valid_choice:
        choice = input(message).strip().lower()
        valid_choice = choice in options
        if not valid_choice:
            print(f"Not a valid option. Valid options: {options}")
    return choice

#################################
# Main steganography functions ##
#################################


def encode_message(cover_image, message):
    """
    Use the least significant bit algorithm to conceal a message in a
    cover image.
    """
    width, height = cover_image.size
    # A three colour channel bitmap image can store a maximum of 3 * the number
    # of pixels bits of data using the LSB algorithm
    max_bits = width * height * 3
    stego_image = Image.new(cover_image.mode, (width, height))
    message_bits = string_to_bits(message)
    number_of_bits = len(message_bits) + 32
    # Check that the message can fit into the image, accounting for 32 bits
    # encoding the message length
    if number_of_bits > max_bits:
        print("\nThe text is too long to be stored in the image file.")
        print("Quitting...")
        return
    # Encode the length of the message in the first 32 bits. This means the
    # maximum length of message is 2^31 - 1 bits in length, assuming a large
    # enough image file could be found
    binary_length = format(number_of_bits, "032b")
    message_bits = binary_length + message_bits
    # This keeps track of the position in message_bits
    current_bit = 0
    pixels = cover_image.getdata()
    stego_pixels = [(0, 0, 0)] * len(pixels)
    for i, pixel in enumerate(pixels):
        rgb = []
        # Replace the lsb of each colour channel until all message bits are
        # stored, then write the new RGB values to the corresponding pixel
        # of the stego image
        for colour_channel in pixel:
            if current_bit < number_of_bits:
                replacement_bit = int(message_bits[current_bit])
                colour_channel = replace_lsb(colour_channel, replacement_bit)
                current_bit += 1
            rgb.append(colour_channel)
        stego_pixels[i] = (rgb[0], rgb[1], rgb[2])
    stego_image.putdata(stego_pixels)
    return stego_image


def decode_message(stego_image):
    """
    Recover a message stored in an image using the least significant bit
    algorithm.
    """
    width, height = stego_image.size
    # An empty string in which to hold the message bits
    message_bits = ""
    current_bit = 0
    number_of_bits = width * height * 3
    pixels = stego_image.getdata()
    for pixel in pixels:
        for colour_channel in pixel:
            message_bits += str(recover_lsb(colour_channel))
            current_bit += 1
            # Read the length of the message
            if current_bit == 32:
                number_of_bits = int(message_bits, 2)
                message_bits = ""
            elif current_bit >= number_of_bits:
                message = bits_to_string(message_bits)
                return message
    return ""


def main():
    """
    Main entry point for the program. Ask the user whether they would like to
    encode data or decode an image and pass the program onto the corresponding
    function.
    """
    # This code is taken directly from the documentation for pyinstaller,
    # which is used to compile this program into an executable. This code
    # finds the directory from which program is being run, regardless of
    # whether it is being run as an executable (i.e. "frozen") or as a script.
    if getattr(sys, "frozen", False):
        # Get the parent directory of the executable
        bundle_dir = os.path.abspath(os.path.join(sys.executable, os.pardir))
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    options = ["encode", "decode"]
    user_choice = get_user_choice(("Which program would you like to run? "
                                  + "Options: [encode, decode]: "), options)

    if user_choice == options[0]:
        main_encode(bundle_dir)
    else:
        main_decode(bundle_dir)

    input("Press enter to exit: ")


def main_encode(bundle_dir):
    """
    Hide the contents of a text file or user-specified string in an image.

    This function handles user input and deals with file input and output,
    while encode_message() handles the steganography.
    """
    print("You have chosen to encode.\n")
    # Have user choose whether to read text in from a file or to enter it
    # manually in the console
    text_input_options = ["yes", "y", "no", "n"]
    text_input_choice = get_user_choice(("Would you like to read text from"
                                         + " a file? [yes/no]: "),
                                        text_input_options)

    if text_input_choice == "yes" or text_input_choice == "y":
        text_file_name = file_from_user(("Enter the name of the text file you "
                                         + "would like to use: "),
                                        bundle_dir)
        text_file = open(text_file_name, "r")
        # Read text from file into a single string
        input_text = "".join(text_file.readlines())
        text_file.close()
    else:
        input_text = input("Enter the text to be hidden here: ")

    image_file_name = file_from_user(("Enter the name of the image file you "
                                      + "would like to use: "), bundle_dir)
    cover_image = Image.open(image_file_name)
    stego_image_path = os.path.join(bundle_dir, "stego_image.bmp")
    stego_image = encode_message(cover_image, input_text)
    if stego_image:
        stego_image.save(stego_image_path, format="bmp")
        print(f"Stego image written to {stego_image_path}.")


def main_decode(bundle_dir):
    """
    Read a message hidden in a provided image file and write it to a file.
    This function handles user input and file input and output while delegating
    the work of extracting the hidden message to decode_message().
    """
    print("You have chosen to decode.\n")
    stego_image_file = file_from_user(("Enter the name of the stego-image file"
                                       + "you would like to use: "),
                                      bundle_dir)
    output_file_name = input("Enter the name of the output text file: ")
    output_file_path = os.path.join(bundle_dir, output_file_name)
    try:
        output_file = open(output_file_path, "w")
    except OSError:
        print(f"Unable to write to {output_file_path}.")
        return
    stego_image = Image.open(stego_image_file)
    message = decode_message(stego_image)
    output_file.write(message)
    print(f"Output written to {output_file_path}.")
    output_file.close()


if __name__ == "__main__":
    main()
