const config = {
    apiKey: "AIzaSyC9uAZiNr9tAg4Y_Vc3xvlpFsCVBB2goEw",
    authDomain: "eminent-airport-148108.firebaseapp.com",
    databaseURL: "https://eminent-airport-148108.firebaseio.com",
    projectId: "eminent-airport-148108",
    storageBucket: "eminent-airport-148108.appspot.com",
    messagingSenderId: "994857141623",
    appId: "1:994857141623:web:a3fcca47e0a59f0f984d72"
};

firebase.initializeApp(config);
let storage = firebase.storage();

function uploadImage() {
    const parentDiv = this.parentElement;
    const folder = this.getAttribute("data-folder");

    let file = parentDiv.querySelectorAll("input[type=file]")[0].files[0];
    if (file === undefined) {
        alert('Aucun fichier spécifié.');
        return
    }
    // Show the progress bar
    let progressbar = parentDiv.querySelectorAll("progress")[0];
    progressbar.style.display = "inline";

    let storageRef = storage.ref();
    let date = new Date();
    let path = 'media/' + folder + '/' + date.getFullYear() + '/' + (date.getMonth() +1)  + '/' + date.getDate() + '/' + file.name;
    let thisref = storageRef.child(path).put(file);
    thisref.on('state_changed', function (snapshot) {
        progressbar.value = (snapshot.bytesTransferred / snapshot.totalBytes) * 100 ;
        switch (snapshot.state) {
            case firebase.storage.TaskState.PAUSED: // or 'paused'
                console.log('Upload is paused');
                break;
            case firebase.storage.TaskState.RUNNING: // or 'running'
                //console.log('Upload is running');
                break;
        }
    }, function (error) {
        alert("Une erreur s'est produite : " + error.message)
    },
    function () {
        // Upload completed successfully, now we can get the download URL
        thisref.snapshot.ref.getDownloadURL().then(function (downloadURL) {
            progressbar.style.display = "none";
            parentDiv.querySelectorAll("input[type=text]")[0].value = path;
            parentDiv.querySelectorAll("img")[0].src = downloadURL;
            parentDiv.querySelectorAll("img")[0].style.display = 'block';
        });
    });
}

(function($) {
    $(document).ready(function () {
        // Load all images from Firebase
        let images = document.getElementsByClassName('display');
        for (let i = 0; i < images.length; i++) {
            let image = images[i];
            if (image.dataset.url !== 'None') {
                let imagesRef = storage.ref(image.dataset.url);
                imagesRef.getDownloadURL().then(function (url) {
                    image.src = url;
                }).catch(function (error) {
                    alert('Erreur :' + error.message);
                });
            } else {
                image.style.display = 'none';
            }
        }

        // Init upload image buttons
        buttons = document.getElementsByClassName('uploadFirebaseImage');
        Array.from(buttons).forEach(function (element) {
            element.addEventListener('click', uploadImage);
        });
    });
}(django.jQuery))
