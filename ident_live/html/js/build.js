console.log("Build v. 1.0 c. IDent, MARLIN, brahma");



/* Data API */
let GetRunIDs = new Promise(function (myResolve) {
    
    // get folder names

});


fetch('data/global_out.json')
    .then((response) => response.json())
    .then((json) => console.log(json));


/* GUI */

GetRunIDs.then((value) => {
    alert(value);
})

/* Run */

