var config = {
    apiKey: "AIzaSyBZvRl1Q35AH9j4vYKwTM5YYMUZp6HAjLo",
    authDomain: "eminent-airport-148108.firebaseapp.com",
    databaseURL: "https://eminent-airport-148108.firebaseio.com",
    projectId: "eminent-airport-148108",
    storageBucket: "eminent-airport-148108.appspot.com",
    messagingSenderId: "994857141623"
};

firebase.initializeApp(config);
var storage = firebase.storage();

var img = document.getElementById('display');
if (img.dataset.url !== 'None') {
    var imagesRef = storage.ref(img.dataset.url);
    imagesRef.getDownloadURL().then(function(url) {
        img.src = url;
    }).catch(function(error) {
        alert('Erreur :' + error);
    });
}

function uploadImage(folder) {
    // Show the progress bar
    document.getElementById("progressbar").style.display = "inline";

    var file = document.getElementById("files").files[0];
    var storageRef = storage.ref();
    var date = new Date();
    var path = 'media/' + folder + '/' + date.getFullYear() + '/' + (date.getMonth() +1)  + '/' + date.getDate() + '/' + file.name;
    var thisref = storageRef.child(path).put(file);
    thisref.on('state_changed', function (snapshot) {
        document.getElementById("progressbar").value = (snapshot.bytesTransferred / snapshot.totalBytes) * 100 ;
        switch (snapshot.state) {
            case firebase.storage.TaskState.PAUSED: // or 'paused'
                console.log('Upload is paused');
                break;
            case firebase.storage.TaskState.RUNNING: // or 'running'
                //console.log('Upload is running');
                break;
        }
    }, function (error) {
        alert("Une erreur s'est produite : " + error)
    },
    function () {
        // Upload completed successfully, now we can get the download URL
        thisref.snapshot.ref.getDownloadURL().then(function (downloadURL) {
            document.getElementById("progressbar").style.display = "none";
            document.getElementById("url").value = path;
            document.getElementById("display").src = downloadURL;
        });
    });
}