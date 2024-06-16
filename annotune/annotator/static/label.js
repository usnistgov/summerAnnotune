document.addEventListener('DOMContentLoaded', function () {
        
    const manualsubmit = document.getElementById('manualLabelSubmit');
    const documentText = document.getElementById('documentText');
    const userId = 0;
    var firstManualLabelInput = document.getElementById("firstManualLabelInput");
    var secondManualLabelInput = document.getElementById("secondManualLabelInput");
    var thirdManualLabelInput = document.getElementById("thirdManualLabelInput");
    const nextButton = document.getElementById('nextButton');
    let document_id = document.getElementById('document_id');
    var pageStartDiv = document.getElementById('pageStartTime');
    let pageStart = document.getElementById('pageStartTime').innerText;

    
    

    let documentsData = [];
    let currentIndex = -1;
    

    function sendData() {
        
        const label1 = firstManualLabelInput.value.trim();
        const label2 = secondManualLabelInput.value.trim();
        const label3 = thirdManualLabelInput.value.trim();
        const labels = label1+"and"+label2+"and"+label3;
        console.log(labels)
        const documentId = document.getElementById('document_id').textContent.trim();
        const now = new Date();
        const elapsedPageTime = now - pageStartTime;
        let mm = Math.floor(elapsedPageTime / 1000) % 60;



        // documentId = document_id.textContent;


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
                console.log('Success:', data);
                documentText.textContent = data.textDocument;
                document_id.textContent = data.document_id;
                // buttons.forEach(button => button.disabled=false);
                
                firstManualLabelInput.value ="";
                secondManualLabelInput.value="";
                thirdManualLabelInput.value="";
                // manualsubmit.disabled=true;
                DocumentAlert(data.document_id);
            })
            .catch(error => console.error('Error:', error));
    }

    manualsubmit.addEventListener('click', sendData);


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



    // function checkButtonEnabled() {
    //     const manualsubmit = document.getElementById('manualLabelSubmit');
    //     if ((label1Value===0) || (label2Value ===0) ||(label3Value ===0)){
    //     manualsubmit.disabled = true;
    //     }
    //     else {
    //     manualsubmit.disabled = false;
    //     }
    // };


    // let label1Value=0;
    // let label2Value=0;
    // let label3Value=0;

    // firstManualLabelInput.addEventListener("input", (e) => {
    //     label1Value = e.target.value.length;
    //     manualsubmit.disabled=true;
    //     checkButtonEnabled();
    // });

    // secondManualLabelInput.addEventListener("input", (e) => {
    //     label2Value = e.target.value.length;
    //     manualsubmit.disabled=true;
    //     checkButtonEnabled();
    // });
    // thirdManualLabelInput.addEventListener("input", (e) => {
    //     label3Value = e.target.value.length;
    //     manualsubmit.disabled=true;
    //     checkButtonEnabled();
    // });


    nextButton.addEventListener('click', function (event) {
        event.preventDefault();
            // No next document, call skip_document view
            fetch('/get_all_documents/')
            .then(response => response.json())
            .then(data => {
                documentsData = data.document_ids;
                // 
                // console.log(data)


                // Load the previous document
                if (currentIndex > 0) {
                    currentIndex--;

                    loadDocument(documentsData[currentIndex]);
                    DocumentAlert(documentsData[currentIndex]);
    
                }
                else{
                    fetch('/skip_document/')
                    .then(response => response.json())
                    .then(data => {
                        currentIndex =  - 1;
                        loadDocument(data.document_id);
                        DocumentAlert(data.document_id);
                    }
                        )}
                    
                    });
                });


            
            


    previousButton.addEventListener('click', function (event) {
        event.preventDefault();

        fetch('/get_all_documents/')
            .then(response => response.json())
            .then(data => {
                documentsData = data.document_ids;
                console.log(data);
                // pageStartDiv.innerText = data.pageStart;
                
                

                // Load the previous document
                if (currentIndex < documentsData.length - 1) {
                    currentIndex++;
                    console.log('Current Index (Previous):', currentIndex);
                    const documentData = documentsData[currentIndex];
                    loadDocument(documentData);
                    DocumentAlert(documentData);

                   
                }
            })
            .catch(error => console.error('Error fetching documents data:', error));
        });

    function loadDocument(index){
        const url = `/fetch_data/${userId}/${index}/`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    
                    console.log('Success:', data);
                    documentText.textContent = data.textDocument;
                    document_id.textContent = data.document_id;
                    pageStartDiv.innerText = data.pageStart;
                    firstManualLabelInput.value ="";
                    secondManualLabelInput.value="";
                    thirdManualLabelInput.value="";
                
                    
                });
    }

    

    function DocumentAlert(document_id) {
        var alertDiv = document.getElementById('myalert')
        alertDiv.style.display = 'flex'; // Show the alert
        alertDiv.innerText = `You are viewing document ${document_id}`;
        // console.log(alert_value);
        setTimeout(() => {
            alertDiv.style.display = 'none'; // Hide the alert after 3 seconds
        }, 3000);
    
    }

    const buttonsContainer = document.getElementById('suggestedLabels');
    const buttons = buttonsContainer.querySelectorAll('.btn');
    // console.log(buttons); // Debugging line to ensure buttons are selected
    const inputs = [
        document.getElementById('firstManualLabelInput'),
        document.getElementById('secondManualLabelInput'),
        document.getElementById('thirdManualLabelInput')
    ];

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            // console.log(`Button ${button.value} clicked`); // Debugging line to ensure event listener is attached
            for (let input of inputs) {
                if (!input.value) {
                    input.value = button.innerText;
                    // console.log(`Input filled with ${button.innerText}`); // Debugging line to check input fill
                    break;
                }
            }

        });
    });




});