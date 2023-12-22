import xml.etree.ElementTree as ET

def get_coverage_percentage(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Assuming the coverage percentage is stored in the line-rate attribute
    coverage = float(root.attrib.get('line-rate', 0)) * 100

    return coverage

# Example usage:
xml_file_path = 'coverage.xml'  # Update with the actual path to your coverage report file
percentage = get_coverage_percentage(xml_file_path)
print(f'Coverage Percentage: {percentage}%')