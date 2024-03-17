export class Timers {

    static _db = {} // internal database of all timers

    static get(name){
        return(Timers._db[name])
    }

    static setAll(state, donowtoo=false, names=null){
        if (names === null){
            names = Object.keys(Timers._db)
        }
        console.log("Setting timers [", state , "]: ", names.join(", "))
        // state MUST be either pause or resume
        for (var n=0; n < names.length; n++){
            Timers.get(names[n])[state](donowtoo)
        }
    }

    constructor(name, do_func, millisecs) {
        this.timer = null
        this.task = do_func
        this.ms = millisecs
        this.resume()
        Timers._db[name] = this
    }

    resume(donowtoo=false){
        if (this.timer === null){
            this.timer = setInterval(this.task, this.ms);
            if (donowtoo){
                this.task()
            }
        }
    }

    pause() {
        if (this.timer !== null){
            clearInterval(this.timer);
            this.timer = null
        }
    }
}