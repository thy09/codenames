var codenames = {
    load_words : function(words){
        for (var i=0;i<25;i++){
            var word = $("<div></div>").addClass("word").attr("id","w"+i).html("<p>"+words[i]+"</p>");
            $(".words").append(word);
        }
        $(".words").append($("<div style='clear:both'></div>"));
    },
    load_distribution: function(dist){
        var words = this.game.words;
        for (var i=0;i<25;i++){
            $("#w"+i).addClass(dist[i]);
            //var block = $("<div></div>").addClass("block "+dist[i]);
            var block = $("<div></div>").addClass("word").addClass("block "+dist[i]).attr("id","wb"+i).html("<p>"+words[i]+"</p>");
            $(".captain_words").append(block);
        }
        $(".captain_words").append($("<div style='clear:both'></div>"));
    },
    load_opened: function(opened){
        console.log(opened);
        console.log(this.game.dist);
        for (var i=0;i<25;i++){
            $("#w"+i).removeClass("open");
            $("#wb"+i).removeClass("open");
            if (opened[i] && this.game.dist[i] == 'g'){
                $("#w"+i).addClass("open");
                $("#wb"+i).addClass("open");
            }
            if (opened[i] == 3){
                $("#w"+i).addClass("open");
                $("#wb"+i).addClass("open");
                if (this.game.dist[i] == 'r' || this.game.dist[i] == 'b'){
                    $("#w"+i+" img").attr("src", this.game.g_url);
                    $("#wb"+i+" img").attr("src", this.game.g_url);
                }
            }
            if (opened[i] == this.game.group){
                $("#w"+i).addClass("open");
            }
            if (opened[i] == 3 - this.game.group){
                $("#wb"+i).addClass("open");
            }
        }
    },
    load_game : function(game){
        this.game = game;
        this.load_words(game.words);
        this.load_distribution(game.dist);
        this.game.x_url = "./static/x.jpg";
        this.game.p_url = "./static/p0.jpg";
        this.game.g_url = "./static/g0.jpg";
        //this.load_opened(game.opened);
        if (game.start == 'b'){
            $(".captain").addClass("b");
            $("#new_game").attr("href","/captain?start=r");
        }else{
            $("#new_game").attr("href","/captain?start=b");
        }
        for (var i=0;i<this.game.discussion.length;i++){
            $(".discussion").prepend("<p>"+unescape(this.game.discussion[i])+"</p>")
        }
    },
    sock_init : function(){
        this.sock.emit("join",{"id":this.game.id});
        this.sock.on("discussion", function(msg){
            console.log(msg);
            $(".discussion").prepend("<p>"+ unescape(msg.data) +"</p>");
        });
        this.sock.on("open", function(msg){
            console.log(msg);
            var idx = msg.data.idx;
            var val = msg.data.val;
            if (val == codenames.game.group || val == 3){
                $("#w"+msg.data.idx).addClass("open");
            }
            if (val == 3 - codenames.game.group || val == 3){
                $("#wb"+msg.data.idx).addClass("open");
            }
            if (val == 3 && (codenames.game.dist[idx] == 'r' || codenames.game.dist[idx] == 'b')){
                $("#w"+idx+" img").attr("src", codenames.game.g_url);
                $("#wb"+idx+" img").attr("src", codenames.game.g_url);
                console.log("Change URL:" + idx);
            }
            codenames.game.opened[idx] = val;
        });
    },
    show_words : function(){
        var colors = ["r","g","b","z","y","x"];
        for (var i in colors){
            $(".words .word."+colors[i]).removeClass(colors[i]).addClass("p");           
        }
    },
    be_one : function(){
        if (!confirm("确定选择一队？")){
            return;
        }
        this.game.group = 1;
        $(".captain-btns").remove();
        $(".word").addClass("show");
        var dist = this.game.dist;
        for (var i=0;i<dist.length;i++){
            var d = dist[i];
            if (d == 'b' || d == 'g'){
                $("#w"+i).append("<img src='"+this.game.g_url+"'></img>");                 
            }
            if (d == 'r' || d == 'p' || d == "y"){
                $("#w"+i).append("<img src='"+this.game.p_url+"'></img>");                                
            }
            if (d == "x" || d == 'z'){
                $("#w"+i).append("<img src='"+this.game.x_url+"'></img>");                                
            }
        }
        this.show_words();
        $(".block.r").removeClass("r").addClass("g");
        $(".block.y").removeClass("y").addClass("x");
        $(".block.z").removeClass("z").addClass("p");
        $(".block.b").removeClass("b").addClass("p");
        $(".block.p").append("<img src='"+this.game.p_url+"'></img>");
        $(".block.x").append("<img src='"+this.game.x_url+"'></img>");
        $(".block.g").append("<img src='"+this.game.g_url+"'></img>");
        this.add_click();
        this.load_opened(this.game.opened);
        $(".captain_words").removeClass("hidden");
    },
    be_two : function(){
        if (!confirm("确定选择二队？")){
            return;
        }
        this.game.group = 2;
        $(".captain-btns").remove();
        this.reverse();
        $(".word").addClass("show");
        var dist = this.game.dist;
        for (var i=0;i<dist.length;i++){
            var d = dist[i];
            if (d == 'r' || d == 'g'){
                $("#w"+i).append("<img src='"+this.game.g_url+"'></img>");                 
            }
            if (d == 'b' || d == 'p' || d == "z"){
                $("#w"+i).append("<img src='"+this.game.p_url+"'></img>");                                
            }
            if (d == "x" || d == 'y'){
                $("#w"+i).append("<img src='"+this.game.x_url+"'></img>");                                
            }
        }
        this.show_words();
        $(".block.b").removeClass("b").addClass("g");
        $(".block.z").removeClass("z").addClass("x");
        $(".block.y").removeClass("y").addClass("p");
        $(".block.r").removeClass("r").addClass("p");
        $(".block.p").append("<img src='"+this.game.p_url+"'></img>");
        $(".block.x").append("<img src='"+this.game.x_url+"'></img>");
        $(".block.g").append("<img src='"+this.game.g_url+"'></img>");
        this.add_click();
        this.load_opened(this.game.opened);
        $(".captain_words").removeClass("hidden");
    },
    add_click : function(){
        $(".words .word").each(function(idx,elm){
            $(elm).click(function(){
                var idx = parseInt($(elm).attr("id").substr(1));
                if (!confirm("确定点开 "+this.game.words[idx] + " 这个代号?")){
                    return;
                }
                this.game.opened[idx] = 1;
                var data = {"id":this.game.id,"idx":idx, "group":this.game.group};
                this.sock.emit("open",{"data":data});
            }.bind(this));
        }.bind(this));
    },
    reverse : function(){
        var words = $(".words .word");
        words.remove();
        for (var i=0;i<words.length;i++){
            $(".words").prepend(words[i]);
        }
        var blocks = $(".block");
        for (var i=0;i<blocks.length;i++){
            $(".captain_words").prepend(blocks[i]);
        }
    },
    be_captain : function(){
        if (!confirm("确定是队长？队长会看到答案哦！")){
            return;
        }
        $(".word").addClass("show");
        $(".word").each(function(idx,elm){
            $(elm).click(function(){
                if (!confirm("确定点开 "+this.game.words[idx] + " 这个代号?")){
                    return;
                }
                this.game.opened[idx] = 1;
                var data = {"id":this.game.id,"idx":idx};
                this.sock.emit("open",{"data":data});
            }.bind(this));
        }.bind(this));
        $(".captain").removeClass("hidden");
    },
    submit : function(){
        var name = $("#name").val();
        var sentence = $("#sentence").val();
        if (name == ""){
            alert("请输入姓名");
            return;
        }
        if (sentence == ""){
            alert("请输入发言");
            return;
        }
        var data = {"id":this.game.id,"say":escape(name+": "+sentence)};
        console.log(data);
        this.sock.emit("update",{"data":data});
        $("#sentence").val("");
    },
    sock : null,
}
