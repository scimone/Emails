import re
from difflib import SequenceMatcher

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfrw import PdfReader, PdfDict, PdfWriter


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
            substrings = split_string(preceding_field)
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

                max_similarity_score = 0
                max_similarity_key = None

                for key in field_data:
                    similarity_score = calculate_string_similarity_weighted(key, field_name)

                    if similarity_score > 0.6 and similarity_score > max_similarity_score:
                        max_similarity_score = similarity_score
                        max_similarity_key = key

                if max_similarity_key is not None:
                    print(max_similarity_score, max_similarity_key, field_name)
                    annotation.update(PdfDict(PdfDict(AP=field_data[max_similarity_key], V=field_data[max_similarity_key])))

    # Write the filled form to the output PDF
    PdfWriter().write(output_path, template_pdf)


def transform_string(input_string):
    """
    Transforms an input string by removing repeating whitespaces, newline characters,
    special characters, and converting it to lowercase.

    Args:
        input_string (str): The input string to transform.

    Returns:
        str: The transformed string.
    """
    transformed_string = re.sub(r'\s+', '  ', input_string)
    transformed_string = transformed_string.replace('\n', '')
    transformed_string = re.sub(r'[^a-zA-Z0-9 ]', '', transformed_string).lower()
    return transformed_string


def calculate_string_similarity_levenshtein(str1, str2):
    """
    Calculates the similarity score between two strings using the Levenshtein distance algorithm.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        float: The similarity score between 0 and 1.
    """
    similarity_score = SequenceMatcher(None, str1, str2).ratio()
    return similarity_score


def calculate_string_similarity_words(str1, str2):
    """
    Calculates the similarity score between two strings based on the ratio of common characters.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        float: The similarity score between 0 and 1.
    """
    str1_length = len(str1)
    common_chars = sum(1 for char in str1 if char in str2)
    similarity_score = common_chars / str1_length
    return similarity_score


def calculate_string_similarity_weighted(str1, str2):
    """
    Calculates the weighted similarity score between two strings using word similarity,
    Levenshtein coefficient, and exact match.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.

    Returns:
        float: The weighted similarity score between 0 and 1.
    """
    str1, str2 = transform_string(str1), transform_string(str2)
    word_similarity = calculate_string_similarity_words(str1, str2)
    levenshtein_similarity = calculate_string_similarity_levenshtein(str1, str2)
    exact_match = ' ' + str1 in str2
    similarity_score = 2 / 5 * word_similarity + 2 / 5 * levenshtein_similarity + 1 / 5 * exact_match
    return similarity_score


def split_string(field_name):
    """
    Splits the first field value into substrings.

    Args:
        field_name (str): The first field name.

    Returns:
        list: List of substrings from the first field value.
    """

    def initialize_pdfminer(input_path):
        fp = open(input_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        return pages, device, interpreter

    pages, device, interpreter = initialize_pdfminer(input_pdf_path)
    substrings = None

    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                line = lobj.get_text()
                if calculate_string_similarity_levenshtein(transform_string(field_name), transform_string(line)) > 0.85:
                    substrings = re.split(r'\s{2,}', line)
                    substrings = [substring for substring in substrings if substring.strip()]
    return substrings


if __name__ == '__main__':
    input_pdf_path = 'data/PROCURA SPECIALE editabile_2.pdf'
    output_pdf_path = 'data/output_form.pdf'
    user_profile = {
        'nome': 'name',
        'cognome': 'surname',
        'il': 'birth date',
        'provincia': 'birth province',
        'a': 'birth city',
        'residente a': 'city of residency',
        'cf': 'codice fiscale',
        'pec': 'pec address',
        'codice fiscale': 'codice fiscale',
        'cap': 'cap',
        'via': 'street name',
        'n': 'street number',
        'piazza': 'street name',
        'sottoscritt': 'full name',
        'tel': 'home phone',
        'cel': 'cell phone',
        'mail': 'email address',
        'email': 'email address',
    }

    fill_pdf_form(input_pdf_path, output_pdf_path, user_profile)
