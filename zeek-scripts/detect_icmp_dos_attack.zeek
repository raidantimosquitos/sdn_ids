@load base/frameworks/notice

module PingFloodDetection;

export {
    ## Threshold for the number of ICMP echo requests within the observation window
    option ping_threshold = 100;  # Adjust this threshold as needed

    ## Time window (in seconds) for detecting the flood
    option observation_window = 10 secs;  # Observe for 15 seconds

    ## The URL of the controller for sending alerts
    option controller_url = "http://192.168.100.3:6633";
}


## Define custom notice type for PingFlood
redef enum Notice::Type += { PingFlood };

## Store the number of ICMP echo requests from each source IP
global icmp_request_count: table[string] of count &create_expire=observation_window;

## Function to send a HTTP POST request to the controller using curl
function send_http_alert(url: string, payload: string) {
    local command = fmt("curl -X POST -H 'Content-Type: application/json' -d '%s' '%s' &", payload, url);
    print command;
    system(command);
}

## Schedule the first execution
event zeek_init(){
    print "Ping Flood Detection script initialized";
}

## Event handler to track ICMP echo requests
event icmp_echo_request(c: connection, info: icmp_info, id: count, seq: count, payload: string){
    local orig_host = fmt("%s", c$id$orig_h);
    local targ_host = fmt("%s", c$id$resp_h);
    print fmt("ICMP echo request from %s to %s", orig_host, targ_host);

    if (orig_host !in icmp_request_count) {
        icmp_request_count[orig_host] = 0;  # Initialize to 0 if key doesn't exist
    }   
 
    ## Increment the count for the source IP address of the ICMP request
    icmp_request_count[orig_host] += 1;

    ## If the request count exceeds the threshold, generate a notice
    if (icmp_request_count[orig_host] > ping_threshold) {
        local message = fmt("Potential ping flooding detected from %s to %s with %d ICMP echo requests", orig_host, targ_host, icmp_request_count[orig_host]);
	print message;
	
	## Send an alert to the controller
	local alert_payload = fmt("{\"source_ip\": \"%s\", \"destination_ip\": \"%s\", \"request_count\": %d}", orig_host, targ_host, icmp_request_count[orig_host]);
	print alert_payload;
	send_http_alert(controller_url, alert_payload);

        local n: Notice::Info = Notice::Info($note=PingFlood, $msg=message, $identifier=orig_host);
        NOTICE(n);

	## Reset count for the source IP to avoid repeated alerts
	icmp_request_count[orig_host] = 0;
    }
}
