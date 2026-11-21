*** Settings ***
Library  Browser

*** Variables ***
${SERVER}     localhost:5000
${DELAY}      500ms
${HOME_URL}   http://${SERVER}
${RESET_URL}  http://${SERVER}/reset_db
${CREATE_URL}  http://${SERVER}/create
${BROWSER}    chromium
${HEADLESS}   false

*** Keywords ***
Open And Configure Browser
    IF  $HEADLESS == 'true'
        New Browser  browser=${BROWSER}  headless=True
    ELSE
        New Browser  browser=${BROWSER}  headless=False  slowMo=${DELAY}
    END
    New Context
    New Page  about:blank

Reset Todos
    Go To  ${RESET_URL}
