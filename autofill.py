from pdfrw import PdfReader, PdfDict, PdfObject, PdfWriter


def get_field_names(template_pdf):
    """
    Collects all field names from the PDF form.

    Args:
        template_pdf (PdfReader): The PDF form template.

    Returns:
        list: List of field names.
    """
    field_names = []
    for page in range(len(template_pdf.pages)):
        annotations = template_pdf.pages[page]['/Annots']
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget' and '/T' in annotation:
                field_name = annotation['/T'][1:-1]  # Remove parentheses from field name
                field_names.append(field_name.lower())
    print(field_names)
    return field_names


def find_consecutive_indices(substring, string_list):
    """
    Finds the first index of every consecutive appearance or single appearance of a substring within a list of strings.
    Also returns the lengths of consecutive repeating strings.

    Args:
        substring (str): The substring to search for.
        string_list (list): List of strings.

    Returns:
        tuple: Tuple containing two lists - first indices of consecutive or single appearances, and lengths of consecutive repeating strings.
    """
    indices = []
    lengths = []
    consecutive_indices = []
    current_length = 0

    for i, string in enumerate(string_list):
        if substring in string:
            if len(consecutive_indices) == 0 or consecutive_indices[-1] == i - 1:
                consecutive_indices.append(i)
                current_length += 1
            else:
                if len(consecutive_indices) >= 1:
                    indices.append(consecutive_indices[0])
                    lengths.append(current_length)
                consecutive_indices = [i]
                current_length = 1

    if len(consecutive_indices) >= 1:
        indices.append(consecutive_indices[0])
        lengths.append(current_length)

    return indices, lengths


def split_field_value(field_name, field_count):
    """
    Splits the first field value into substrings based on the count of subsequent fields containing 'Testo'.

    Args:
        field_name (str): The first field name.
        field_count (int): The count of subsequent fields containing 'Testo'.

    Returns:
        list: List of substrings from the first field value.
    """
    substrings = field_name.split(' ', field_count + 1)

    # Adjust the number of substrings to match the number of subsequent 'Testo' fields
    if len(substrings) > field_count + 1:
        substrings = substrings[:field_count + 1]
    else:
        substrings.extend([''] * (field_count + 1 - len(substrings)))  # Fill missing substrings with empty strings

    return substrings


def fill_pdf_form(input_path, output_path, field_data):
    """
    Fills the PDF form fields with the provided data.

    Args:
        input_path (str): Path to the input PDF form.
        output_path (str): Path to the output filled PDF form.
        field_data (dict): Dictionary of field names and corresponding values.
    """
    template_pdf = PdfReader(input_path)
    field_names = get_field_names(template_pdf)
    testo_indices, lengths = find_consecutive_indices('testo', field_names)
    if testo_indices:
        for idx, n in zip(testo_indices, lengths):
            # Split the first field before 'Testo' fields into substrings
            preceding_field = field_names[idx - 1]
            substrings = preceding_field.split()
            substrings = [string for string in substrings if len(string) > 1]
            for i in range(n + 1):
                field_names[idx - 1 + i] = substrings[i]

    # Fill the form fields
    j = 0
    for page in range(len(template_pdf.pages)):
        annotations = template_pdf.pages[page]['/Annots']

        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget' and '/T' in annotation:
                field_name = field_names[j]
                j += 1
                for key in field_data:
                    if key.lower() in field_name.lower():
                        # print('!')
                        annotation.update(PdfDict(PdfDict(AP=field_data[key], V=field_data[key])))

    # Write the filled form to the output PDF
    PdfWriter().write(output_path, template_pdf)


if __name__ == '__main__':
    form_data = {
        'nome': 'John',
        'cognome': 'Doe',
        'nat': '01/01/00',
        'provincia': 'Trieste',
        'cf': 'AA123456789',
        'cap': '34121',
        'via': 'Piazza Unità',
        'piazza': 'Piazza Unità',
        'sottoscritt': 'John Doe',
        'tel': '01234',
        'cel': '56789',
        'mail': 'johndoe@example.com'
    }

    input_pdf_path = 'data/PROCURA SPECIALE editabile_2.pdf'
    output_pdf_path = 'data/output_form.pdf'

    fill_pdf_form(input_pdf_path, output_pdf_path, form_data)
