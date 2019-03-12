# Simple zmq multiprocessing function executor.
  
  ### why not rabbitmq ?
  Rabbitmq module is coming soon, i want to see what are the diferences that RMQ is oferring compared to the ZMQ.

  #### 1- Give the zmq_send the function you want to execute and submit.
  #### 2- Run the zmq_server
  #### 3- The recev part will check the zmq queue,check for module to load and will get the function and create a processe for each task to execute it.
  
  ## what does it is support :
  I have tried 4 different functions to execute, example :


        msg = {"modules" :"","executable" :'print "hello world"',"arguments":" "}
        msg = {"modules" :"numpy","executable" :'numpy.sin(1+2)',"arguments":" "}
        msg = {"modules" :"os","executable" :'os.system(ls -all)',"arguments":" "}
        msg = {"modules" :"time","executable" :'time.time()',"arguments":" "}
        
     

    
 
