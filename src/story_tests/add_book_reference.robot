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
${BOOK_URL}       https://example.com/clean-code

*** Test Cases ***
User Can Add A Book Reference To The System
    Go To Home Page
    Fill Book Reference Form
    Submit Reference Form
    Book Reference Should Be Visible In Reference List

*** Keywords ***
Go To Home Page
    Go To    ${HOME_URL}
    Wait For Elements State    form    visible

Fill Book Reference Form
    Fill Text    input[name="name"]            ${BOOK_TITLE}
    Fill Text    input[name="type"]            ${BOOK_TYPE}
    Fill Text    input[name="author"]          ${BOOK_AUTHOR}
    Fill Text    input[name="publish_year"]    ${BOOK_YEAR}
    Fill Text    input[name="url"]             ${BOOK_URL}

Submit Reference Form
    Click    button[type="submit"]
    Wait For Load State    networkidle

Book Reference Should Be Visible In Reference List
    ${page_text}=    Get Text    body
    Should Contain    ${page_text}    ${BOOK_TITLE}
