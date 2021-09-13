from argparse import ArgumentParser, ArgumentTypeError
from email import policy, message_from_file
from pathlib import Path
from typing import List


def extract_attachments(file: Path, destination: Path) -> None:
    print(f'PROCESSING FILE "{file}"')
    with file.open() as f:
        email_message = message_from_file(f, policy=policy.default)
        email_subject = email_message.get('Subject')
        basepath = destination / email_subject
        # ignore inline attachments
        attachments = [item for item in email_message.iter_attachments() if item.is_attachment()]
        if not attachments:
            print('>> No attachments found.')
            return
        for attachment in attachments:
            filename = attachment.get_filename()
            print(f'>> Attachment found: {filename}')
            filepath = basepath / filename
            payload = attachment.get_payload(decode=True)
            if filepath.exists():
                overwrite = input(f'>> The file "{filename}" already exists! Overwrite it (Y/n)? ')
                save_attachment(filepath, payload) if overwrite.upper() == 'Y' else print('>> Skipping...')
            else:
                basepath.mkdir(exist_ok=True)
                save_attachment(filepath, payload)

def save_attachment(file: Path, payload: bytes) -> None:
    with file.open('wb') as f:
        print(f'>> Saving attachment to "{file}"\n')
        f.write(payload)

def get_eml_files_from(path: Path) -> List[Path]:
    return list(path.glob('*.eml'))

def main():
    parser = ArgumentParser(
        usage='python3 %(prog)s [OPTIONS]',
        description='Extracts attachments from EML files',
    )
    parser.add_argument(
        '-s',
        '--source',
        nargs='+',
        type=Path,
        default=get_eml_files_from(Path.cwd()),
        metavar='FILE',
        help='EML file or list of EML files. Default: all EML files in CWD.'
    )
    parser.add_argument(
        '-d',
        '--destination',
        type=Path,
        default=Path.cwd(),
        metavar='PATH',
        help='Path to folder where the attachments will be saved. Default: CWD.'
    )
    args = parser.parse_args()

    eml_files = args.source
    if not eml_files:
        print(f'No EML files found!')

    for file in eml_files:
        extract_attachments(file, destination=args.destination)
    print('Done.')


if __name__ == '__main__':
    main()
