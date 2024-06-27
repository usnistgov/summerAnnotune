document.addEventListener('DOMContentLoaded', function () {
    const manualsubmit = document.getElementById('manualLabelSubmit');
    const documentText = document.getElementById('documentText');
    const userId = document.getElementById("user_id").innerText;
    const firstManualLabelInput = document.getElementById("firstManualLabelInput");
    const secondManualLabelInput = document.getElementById("secondManualLabelInput");
    const thirdManualLabelInput = document.getElementById("thirdManualLabelInput");
    const nextButton = document.getElementById('nextButton');
    const previousButton = document.getElementById('previousButton');
    const document_id = document.getElementById('document_id');
    const pageStartDiv = document.getElementById('pageStartTime');
    let pageStarter = document.getElementById('pageStartTime').innerText;
    let pageStart = dateConvert(pageStarter);
    let documentsData = [];
    let currentIndex = -1;

    // Disable the submit button initially
    manualsubmit.disabled = true;

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function changeAllButtonsCSS() {
        const div = document.getElementById('suggestedLabels');
        const buttons = div.getElementsByTagName('button');
        for (let button of buttons) {
            button.style.backgroundColor = 'rgb(213, 216, 217)';
            button.style.margin = '2px';
        }
    }

    function DocumentAlert(document_id) {
        const alertDiv = document.getElementById('myalert');
        alertDiv.style.display = 'flex'; // Show the alert
        alertDiv.innerText = `You are viewing document ${document_id}`;
        setTimeout(() => {
            alertDiv.style.display = 'none'; // Hide the alert after 3 seconds
        }, 3000);
    }

    function loadDocument(index) {
        const url = `/fetch_data/${userId}/${index}/`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                documentText.textContent = data.textDocument;
                document_id.textContent = data.document_id;
                pageStartDiv.innerText = data.pageStart;
                firstManualLabelInput.value = "";
                secondManualLabelInput.value = "";
                thirdManualLabelInput.value = "";
                manualsubmit.disabled = true; // Disable the submit button when loading a new document
            })
            .catch(error => console.error('Error fetching document:', error));
    }

    function sendData() {
        const label1 = firstManualLabelInput.value.trim();
        const label2 = secondManualLabelInput ? secondManualLabelInput.value.trim() : '';
        const label3 = thirdManualLabelInput ? thirdManualLabelInput.value.trim() : '';

        const labels = [label1, label2, label3].filter(Boolean).join(" and ");

        const documentId = document.getElementById('document_id').textContent.trim();
        const now = new Date();
        pageStarter = pageStartDiv.innerText;
        pageStart = dateConvert(pageStarter);
        const elapsedPageTime = now - pageStart;
        const mm = Math.floor(elapsedPageTime / 1000) % 60;

        const dataToSend = JSON.stringify({
            document_id: documentId,
            label1: label1,
            label2: label2,
            label3: label3,
            user_id: userId,
            response_time: new Date().toISOString()
        });

        fetch(`/submit-data/${documentId}/${labels}/${mm}/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: dataToSend
        })
            .then(response => response.json())
            .then(data => {
                documentText.textContent = data.textDocument;
                document_id.textContent = data.document_id;
                pageStartDiv.innerText = data.pageStart;
                changeAllButtonsCSS();

                if (data.first_label) {
                    document.getElementById(data.first_label).style.backgroundColor = "rgb(0, 195, 248)";
                }
                if (data.second_label) {
                    document.getElementById(data.second_label).style.backgroundColor = "rgb(137, 229, 255)";
                }
                if (data.third_label) {
                    document.getElementById(data.third_label).style.backgroundColor = "rgb(195, 242, 255)";
                }

                firstManualLabelInput.value = "";
                secondManualLabelInput.value = "";
                thirdManualLabelInput.value = "";
                manualsubmit.disabled = true; // Disable the submit button after submitting
                DocumentAlert(data.document_id);
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchDataAndLoadDocuments(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                documentsData = data.document_ids;
                if (currentIndex > 0) {
                    currentIndex--;
                    loadDocument(documentsData[currentIndex]);
                    DocumentAlert(documentsData[currentIndex]);
                } else {
                    fetch('/skip_document/')
                        .then(response => response.json())
                        .then(data => {
                            currentIndex = -1;
                            loadDocument(data.document_id);
                            DocumentAlert(data.document_id);
                        })
                        .catch(error => console.error('Error skipping document:', error));
                }
            })
            .catch(error => console.error('Error fetching documents data:', error));
    }

    manualsubmit.addEventListener('click', sendData);

    nextButton.addEventListener('click', function (event) {
        event.preventDefault();
        fetchDataAndLoadDocuments('/get_all_documents/');
    });

    previousButton.addEventListener('click', function (event) {
        event.preventDefault();
        fetchDataAndLoadDocuments('/get_all_documents/');
    });

    firstManualLabelInput.addEventListener('input', function () {
        manualsubmit.disabled = !firstManualLabelInput.value.trim(); // Enable/disable based on input
    });

    const buttonsContainer = document.getElementById('suggestedLabels');
    const buttons = buttonsContainer.querySelectorAll('.btn');
    const inputs = [firstManualLabelInput, secondManualLabelInput, thirdManualLabelInput];

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            for (let input of inputs) {
                if (!input.value) {
                    input.value = button.innerText;
                    manualsubmit.disabled = !firstManualLabelInput.value.trim(); // Enable/disable based on input
                    break;
                }
            }
        });
    });
});
