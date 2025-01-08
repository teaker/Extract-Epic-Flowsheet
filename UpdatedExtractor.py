import fitz  # PyMuPDF
import re

### THIS IS A WORK IN PROGRESS ###
### 1-7-2024 - THIS SCRIPT SUCCESSFULLY EXTRACTS THE DATETIME HEADER ENTRIES FROM THE FLOWSHEETS.
###          - STILL WORKING ON CLEANLY EXTRACTING ROW/MEASUREMENT NAMES
###          - ONCE ROW NAMES ARE EXTRACTED, NEXT STEP WILL BE TO EXTRACT MEASUREMENT VALUES BY COMPARING THEIR COORDINATES TO DATETIME COLUMN COORDINATES

def extract_text_with_coordinates(pdf_path):
    """
    Extracts text from a PDF, identifies datetimes with precise coordinates,
    and tracks measurement categories.

    Args:
        pdf_path (str): Path to the PDF file.
    """
    # Regex pattern to identify datetime entries in the format "mm/dd/yy tttt"
    datetime_pattern = r"\b\d{2}/\d{2}/\d{2} \d{4}\b"

    # Set to store unique measurement categories
    measurement_categories = set()

    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        full_text = page.get_text()
        if "Flowsheets" not in full_text:
            continue

        print(f"Processing page {page_number + 1}")
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: b[1])  # Sort by y0 (vertical position)

        # Identify the x-coordinate for "Row Name" as a reference for measurement categories
        row_name_x0 = None

        for block in blocks:
            # Unpack the block
            x0, y0, x1, y1, text = block[:4] + (block[4],)

            # Check if "Row Name" is in the block
            if "Row Name" in text:
                row_name_coords = (x0, y0, x1, y1)
                row_name_x0 = x0  # Save the x-coordinate of "Row Name"
                print(f"'Row Name' found at coordinates: {row_name_coords}")

                # Find all datetime entries in the block
                datetimes_in_block = re.findall(datetime_pattern, text)
                datetimes_with_coordinates = []

                for dt in datetimes_in_block:
                    # Use search_for to get the coordinates of the specific datetime
                    matches = page.search_for(dt)
                    for match in matches:
                        # Check if the datetime is in the same row as "Row Name"
                        if abs(match.y0 - y0) < 1:  # Same row if y0 matches
                            datetimes_with_coordinates.append({
                                "datetime": dt,
                                "coordinates": match  # Specific coordinates of the datetime
                            })

                # Print all datetimes with their specific coordinates
                if datetimes_with_coordinates:
                    print(f"Datetimes in the same row as 'Row Name':")
                    for dt_entry in datetimes_with_coordinates:
                        print(f"  - {dt_entry['datetime']} at {dt_entry['coordinates']}")

            # Dynamically identify measurement categories
            elif row_name_x0 is not None and abs(x0 - row_name_x0) < 1:  # Same indentation as "Row Name"
                # Extract the title by splitting on newlines
                title = text.split("\n")[0].strip()
                if title and title not in measurement_categories:
                    measurement_categories.add(title)
                    print(f"New measurement category found: {title}")

    pdf_document.close()

    # Print the list of unique measurement categories
    print("\nUnique Measurement Categories:")
    for category in sorted(measurement_categories):
        print(category)


if __name__ == "__main__":
    # Input PDF file
    pdf_path = r"C:\Users\Teak\Desktop\MJ-UNREDACTED.pdf"

    # Extract text, identify datetimes, and track measurement categories
    extract_text_with_coordinates(pdf_path)
