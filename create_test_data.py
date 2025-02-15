import sqlite3
from add_task import add_task
from initialize_rag import initialize_rag

DB_NAME = "test"


def main():
    con = sqlite3.connect(f"{DB_NAME}.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS metadata")

    initialize_rag(db_name=DB_NAME)

    tasks = [
        "User created a new Word document",
        'User typed the title "Meeting Notes" in the document',
        'User saved the Word document with the name "Meeting Notes - Feb 2025"',
        "User formatted the text to bold in the document",
        "User inserted a table in the Word document",
        "User added a header to the document",
        "User applied a bullet list to a section of the document",
        "User printed the Word document",
        "User inserted a page break in the document",
        "User copied a paragraph of text from one section of the document and pasted it elsewhere",
    ]
    actions = [
        """
            <Click> Opened Microsoft Word from the Windows Start menu. <Click />
            <Click> User clicked on "New" from the File menu. <Click />
            <Text> User selected "Blank Document" from the template options. <Text />
            <Click> User clicked inside the blank document to start typing. <Click />
        """,
        """
            <Text> User clicked inside the blank document to place the cursor. <Text />
            <Text> User typed "Meeting Notes" as the title. <Text />
            <Control> Ctrl + B <Control />
            <Text> User pressed Enter to move to the next line. <Text />
        """,
        """
            <Click> User clicked on the "File" menu in the top-left corner. <Click />
            <Click> User selected "Save As" from the menu. <Click />
            <Click> User selected "This PC" in the Save As dialog. <Click />
            <Text> User typed "Meeting Notes - Feb 2025" in the "File Name" field. <Text />
            <Control> Ctrl + S <Control />
        """,
        """
            <Click> User clicked on the text they want to bold (e.g., "Meeting Notes"). <Click />
            <Control> Ctrl + B <Control />
            <Click> User clicked elsewhere in the document to unselect the bolded text. <Click />
        """,
        """
            <Click> User clicked on the "Insert" tab in the ribbon. <Click />
            <Click> User clicked on the "Table" button in the Insert tab. <Click />
            <Click> User selected a 3x3 table layout from the grid. <Click />
            <Click> User clicked inside a cell in the table to start typing. <Click />
        """,
        """
            <Click> User clicked on the "Insert" tab in the ribbon. <Click />
            <Click> User clicked on "Header" in the Insert tab. <Click />
            <Click> User selected the "Blank" header style from the dropdown. <Click />
            <Text> User typed "Confidential Meeting Notes" as the header. <Text />
            <Click> User clicked outside the header area to return to the body of the document. <Click />
        """,
        """
            <Click> User highlighted the text they want to turn into a bullet list. <Click />
            <Click> User clicked on the "Home" tab in the ribbon. <Click />
            <Click> User clicked on the "Bullets" button in the Paragraph group. <Click />
            <Text> User typed the first item in the list. <Text />
            <Control> Ctrl + Enter <Control />
            <Text> User typed the second item in the list. <Text />
        """,
        """
            <Click> User clicked on the "File" menu. <Click />
            <Click> User selected "Print" from the options. <Click />
            <Click> User selected the printer from the Printer dropdown. <Click />
            <Click> User clicked "Print" to send the document to the printer. <Click />
        """,
        """
            <Click> User clicked on the "Insert" tab in the ribbon. <Click />
            <Click> User clicked on "Page Break" in the Insert tab. <Click />
            <Click> User clicked on the new page to continue typing. <Click />
        """,
        """
            <Click> User highlighted the paragraph they want to copy. <Click />
            <Control> Ctrl + C <Control />
            <Click> User clicked at the location where they want to paste the text. <Click />
            <Control> Ctrl + V <Control />
        """,
    ]

    for task, action in zip(tasks, actions):
        add_task(task, action, db_name=DB_NAME)


if __name__ == "__main__":
    main()
