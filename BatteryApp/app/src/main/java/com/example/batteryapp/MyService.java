package com.example.batteryapp;

import android.app.Service;
import android.content.Intent;
import android.media.MediaPlayer;
import android.os.Binder;
import android.os.IBinder;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

public class MyService extends Service {
    //private CPU_Info myCPUInfo;
    private MediaPlayer player;
    private static String LOG_TAG = "BoundService";


    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        //return super.onStartCommand(intent, flags, startId);
        //myCPUInfo = new CPU_Info();
        /* Do Stuff */
        player = MediaPlayer.create( this, Settings.System.DEFAULT_ALARM_ALERT_URI);
        player.setLooping( true );
        player.start();
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.v(LOG_TAG, "in onDestroy");
        /* STOP executing */
        player.stop();
    }

    @Override
    public IBinder onBind(Intent intent) {
        Log.v(LOG_TAG, "in onBind");
        return null;
    }

    /*public String getCPUUsage() {
        String cpuUse = String.valueOf(myCPUInfo.readCpuFreqNow());
        return cpuUse;
    }*/

}
