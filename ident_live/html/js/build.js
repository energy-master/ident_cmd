console.log("Build v. 1.0 c. IDent, MARLIN, brahma");

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

/* Data API */
let GetRunIDs = new Promise(function (myResolve) {
    
    // get folder names

});


// setInterval(run, 1000);
// setInterval(test, 1000);
run();
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

// Global frame stats
frame_stats = {}
all_environments = []
max_iter = 0;

/* DATA functions */
function BuildFrameStory(data) {
    
   

   
    number_bots = data['number_bots'];
    latest_iter = data['last_bot_iter'];
    
    percentage_complete = (latest_iter / number_bots) * 100;
    // console.log(percentage_complete);
  

    //grab frame data from response
    frame_data = data['frame_overview'];
    d_num = 0;
    //iterate over and group accordingly
    for (const key in frame_data) {
        if (frame_data.hasOwnProperty(key)) {
            max_iter = Math.max(max_iter, key);

            for (var i = 0; i < frame_data[key].length; i++){
                
               
                
                // frame stats
                if (frame_stats.hasOwnProperty(key)) {
                    frame_stats[key].number_hits = frame_stats[key].number_hits + 1;
                    frame_stats[key].bots.push(frame_data[key][i].bot_name);
                    frame_stats[key].envs.push(frame_data[key][i].environment);
                    if (!all_environments.includes(frame_data[key][i].environment)) {
                        all_environments.push(frame_data[key][i].environment);
                    }
                    frame_stats[key].probability = frame_stats[key].number_hits / number_bots;
                    if (frame_stats[key].env_hits.hasOwnProperty(frame_data[key][i].environment)) {
                        frame_stats[key].env_hits[frame_data[key][i].environment] += 1;
                        frame_stats[key].env_prob[frame_data[key][i].environment] = frame_stats[key].env_hits[frame_data[key][i].environment] / number_bots;
                    }
                    else {
                        frame_stats[key].env_hits[frame_data[key][i].environment] = 1;
                        frame_stats[key].env_prob[frame_data[key][i].environment] = 1 / number_bots;
                    }


                }
                else {
                    frame_stats[key] = {
                        'number_hits': 1,
                        'bots': [frame_data[key][i].bot_name],
                        'envs': [frame_data[key][i].environment],
                        'probability': 1 / number_bots,
                        'time': frame_data[key][i].time_stamp,
                        'env_hits': {},
                        'env_prob':{}
                    }
                    frame_stats[key].env_hits[frame_data[key][i].environment] = 1;
                    frame_stats[key].env_prob[frame_data[key][i].environment] = 1 / number_bots;
                    
                }


            }
           
            
        }
    }


    // console.log(frame_stats)
    // console.log(all_environments);
    
    // *** UPDATE GUI ***
    ShowFrameStory();

    ShowActiveSpecImage(latest_iter);

    ShowSimProgress(percentage_complete);

    ShowActivityPlot();
    // *** RESET STATS ***
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
    // console.log(percentage_complete);
    var el = document.getElementById('sim_progress');
    el.innerHTML = html;
    
}

/*
* Chart plotting
*/

function ShowActivityPlot() {
    

    // const config = {
    //     type: 'line',
    //     data: data,
    //     options: {
    //         responsive: true,
    //         plugins: {
    //             title: {
    //                 display: true,
    //                 text: 'Chart.js Line Chart - Cubic interpolation mode'
    //             },
    //         },
    //         interaction: {
    //             intersect: false,
    //         },
    //         scales: {
    //             x: {
    //                 display: true,
    //                 title: {
    //                     display: true
    //                 }
    //             },
    //             y: {
    //                 display: true,
    //                 title: {
    //                     display: true,
    //                     text: 'Value'
    //                 },
    //                 suggestedMin: -10,
    //                 suggestedMax: 200
    //             }
    //         }
    //     },
    // };
   
    // build data -> dataset for each environment
    // const t_vals = Array(max_iter+1).fill(0);
    t_vals = Array.from({ length: max_iter+1 }, (_, index) => index + 1);
    plot_datasets = []
    
    for (const x of all_environments) {
        console.log(max_iter);
        e_vals = Array(max_iter + 1).fill(0);
        _c_ = getRandomColor();
        barColors = Array(max_iter + 1).fill(_c_);
        for (const key in frame_stats) {
            if (frame_stats[key].env_prob.hasOwnProperty(x)) {
                e_vals[key] = frame_stats[key].env_prob[x];
               
            }
        }

        plot_datasets.push({
            label : x,
            data: e_vals,
            borderColor: getRandomColor(),
            backgroundColor:barColors,
            fill: true,
            tension: 1.0

        })


    }
    console.log(max_iter);
    console.log(plot_datasets);


    const myChart = new Chart("activity_profile_plot", {
        type: "bar",
        data: {
            labels: t_vals,
            datasets: plot_datasets,
        },
        options: {
            responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Bot Activity by Env Class'
                        },
                    },
                    interaction: {
                        intersect: false,
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Value'
                            },
                            suggestedMin: 0,
                            suggestedMax: 1
                        }
                    }
          }
      });


    
}