*** Settings ***
Library  SeleniumLibrary

*** Variables ***
${SERVER}  http://localhost:8501

*** Test Cases ***
Verify Streamlit App Loads
    [Documentation]  Verify that the Streamlit app loads and the title is correct
    Open Browser  ${SERVER}  chrome
    Maximize Browser Window
    Sleep  5  # Wait for the app to fully load
    Title Should Be  Streamlit
    [Teardown]  Close Browser
