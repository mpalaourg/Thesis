package com.example.batteryapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;
import android.widget.Toast;

public class Restarter extends BroadcastReceiver {
    /*
     *We override the built-in onRecieve() method in BroadcastReceiver to add the statement which
     * will restart the service. The startService() will not work as intended in and above Android
     * Oreo 8.1, as strict background policies will soon terminate the service after restart once
     * the app is killed. Therefore we use the startForegroundService() for higher versions and show
     * a continuous notification to keep the service running.
     */
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.i("Broadcast Listened", "Service tried to stop");
        Toast.makeText(context, "Service restarted", Toast.LENGTH_SHORT).show();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(new Intent(context, MyService.class));
        } else {
            context.startService(new Intent(context, MyService.class));
        }
    }
}
