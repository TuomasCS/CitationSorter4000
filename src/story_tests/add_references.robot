*** Settings ***
Resource  resource.robot
Suite Setup  Open And Configure Browser
Suite Teardown  Close Browser
Test Setup  Reset Todos

*** Variables ***
${BOOK_TITLE}     Clean Code
${BOOK_TYPE}      Book
${BOOK_AUTHOR}    Robert C. Martin
${BOOK_YEAR}      2008

*** Test Cases ***
Add A Book To The System
    Go To Create Page
    Fill Book Reference Form
    Submit Reference Form
    Book Reference Should Be Visible In Reference List

Add An Article To The System
    Go To Create Page
    Fill Article Reference Form
    Submit Reference Form
    Article Reference Should Be Visible In Reference List

*** Keywords ***
Go To Create Page
    Go To    ${CREATE_URL}
    Wait For Elements State    form    visible

Go To Home Page
    Go To    ${HOME_URL}

Fill Book Reference Form
    Select Options By    id=reference_type    text    Book
    Fill Text    input[name="name"]            ${BOOK_TITLE}
    Fill Text    input[name="author"]          ${BOOK_AUTHOR}
    Fill Text    input[name="publish_year"]    ${BOOK_YEAR}

Fill Article Reference Form
    Select Options By  id=reference_type  text  Article
    Fill Text    input[name="name"]    Software Engineering at Google
    Fill Text    input[name="author"]    Titus Winters
    Fill Text    input[name="publish_year"]    2020
    Fill Text    input[name="volume"]    12
    Fill Text    input[name="pages"]    30-35
    
Submit Reference Form
    Click    button[type="submit"]
    Wait For Load State    networkidle

Book Reference Should Be Visible In Reference List
    ${page_text}=    Get Text    body
    Should Contain    ${page_text}    ${BOOK_TITLE}

Article Reference Should Be Visible In Reference List
    ${page_text}=    Get Text    body
    Should Contain    ${page_text}    Software Engineering at Google