console.log("Build v. 1.0 c. IDent, MARLIN, brahma");



/* Data API */
let GetRunIDs = new Promise(function (myResolve) {
    
    // get folder names

});


setInterval(run, 1000);
setInterval(test, 1000);
function test() {
    console.log("testing");
}

function run() {
   
    console.log("Running");
        fetch('data/global_out.json')
            .then((response) => {
                    return (response.json());
            })
            .then((json_data) => {
                console.log(json_data);
                console.log("building gui");
                BuildFrameStory(json_data);
            });
        
}

frame_stats = {}
frame_stat_obj = {
    'number_hits': 1
}
/* DATA functions */
function BuildFrameStory(data) {
    
   

   
    number_bots = data['number_bots'];
    latest_iter = data['last_bot_iter'];
    
    percentage_complete = (latest_iter / number_bots) * 100;
    console.log(percentage_complete);
  

    //grab frame data from response
    frame_data = data['frame_overview'];
    d_num = 0;
    //iterate over and group accordingly
    for (const key in frame_data) {
        if (frame_data.hasOwnProperty(key)) {
            // console.log(`${key} : ${frame_data[key]}`)

            for (var i = 0; i < frame_data[key].length; i++){
                // console.log(frame_data[key][i]);
                // console.log(frame_data[key].length);
                // console.log(i);


                if (frame_stats.hasOwnProperty(key)) {
                    frame_stats[key].number_hits = frame_stats[key].number_hits + 1;
                    frame_stats[key].bots.push(frame_data[key][i].bot_name);
                    frame_stats[key].envs.push(frame_data[key][i].environment);
                    frame_stats[key].probability = frame_stats[key].number_hits / number_bots;
                }
                else {
                    frame_stats[key] = {
                        'number_hits': 1,
                        'bots': [],
                        'envs': [],
                        'probability': 1 / number_bots,
                        'time': frame_data[key][i].time_stamp
                        
                    }
                }


            }
           
            
        }
    }


    // console.log(frame_stats)
    
    // update gui
    ShowFrameStory();

    ShowActiveSpecImage(latest_iter);

    ShowSimProgress(percentage_complete);

    frame_stats = {}

}


/* GUI */

GetRunIDs.then((value) => {
    alert(value);
})

/* Run */

// var sample = new Spectrogram('data/input.wav', "#vis", {
//     width: 600,
//     height: 300,
//     colorScheme: ['#440154', '#472877', '#3e4a89', '#31688d', '#26838e', '#1f9e89', '#36b778', '#6dcd59', '#b4dd2c', '#fde725'],
//     minFrequency: 100,
//     maxFrequency: 145000,
//     sampleSize : 256
// });

function ShowFrameStory() {

    html = `
     <table class="table">

            <thead>
                <tr>
                    <th scope="col">Frame #</th>
                    <th scope="col">Time Stamp</th>
                     <th scope="col">Number Hits</th>
                    <th scope="col">Probability<th>
                    <!-- <th scope="col">Handle</th> -->
                </tr>
            </thead>
    
    `;
    for (const key in frame_stats) {

        frame_data = frame_stats[key];
        prob = (frame_stats[key]['probability']) * 100;
        html += `<tr><td>${key}</td><td>${frame_stats[key]['time']}</td><td>${frame_stats[key]['number_hits']}</td>
        <td>
        
            <div class="progress">
  <div class="progress-bar" role="progressbar" style="width: ${prob}%" aria-valuenow="${prob}" aria-valuemin="0" aria-valuemax="100"></div>
</div>
        
        </td></tr>`
        

    }

    html += `<table>`

    var el = document.getElementById('main_story');
    el.innerHTML = html;

    
}
// ShowActiveSpecImage();

function ShowActiveSpecImage(latest_iter) {
    
   

    html = `
    <img class = "img-fluid" src="data/active_spectrogram${latest_iter}.png" alt="Active Spectrogram / Decision Overlay" >
    `;

    var el = document.getElementById('active_spec_image');
    el.innerHTML = html;
}

function ShowSimProgress(percentage_complete) {
    // sim_progress
    html = ` <div class="progress">
    <div class="progress-bar" role="progressbar" style="width: ${percentage_complete}%" aria-valuenow="${percentage_complete}" aria-valuemin="0" aria-valuemax="100"></div>
    </div>`
    console.log(percentage_complete);
    var el = document.getElementById('sim_progress');
    el.innerHTML = html;
    
}