let config = {
    apiKey: "AIzaSyBZvRl1Q35AH9j4vYKwTM5YYMUZp6HAjLo",
    authDomain: "eminent-airport-148108.firebaseapp.com",
    databaseURL: "https://eminent-airport-148108.firebaseio.com",
    projectId: "eminent-airport-148108",
    storageBucket: "eminent-airport-148108.appspot.com",
    messagingSenderId: "994857141623"
};

firebase.initializeApp(config);
let storage = firebase.storage();

// Load all images from Firebase
let images = document.getElementsByClassName('display');
for(let i=0; i < images.length; i++) {
    let image = images[i];
    if (image.dataset.url !== 'None') {
        let imagesRef = storage.ref(image.dataset.url);
        imagesRef.getDownloadURL().then(function(url) {
            image.src = url;
        }).catch(function(error) {
            alert('Erreur :' + error.message);
        });
    }
}

function uploadImage(value, folder) {
    // Show the progress bar
    let progressbar = document.getElementById(value).querySelectorAll("progress")[0];
    console.log(progressbar);
    progressbar.style.display = "inline";

    let file = document.getElementById(value).querySelectorAll("input[type=file]")[0].files[0];
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
            document.getElementById(value).querySelectorAll("input[type=text]")[0].value = path;
            document.getElementById(value).querySelectorAll("img")[0].src = downloadURL;
        });
    });
}