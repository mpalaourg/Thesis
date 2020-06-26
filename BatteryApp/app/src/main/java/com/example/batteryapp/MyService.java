package com.example.batteryapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.media.MediaPlayer;
import android.os.Binder;
import android.os.Build;
import android.os.IBinder;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;

public class MyService extends Service {
    //private CPU_Info myCPUInfo;
    private MediaPlayer player;
    private static String LOG_TAG = "BoundService";

    @Override
    public void onCreate() {
        super.onCreate();
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.O)
            startMyOwnForeground();
        else
            startForeground(1, new Notification());
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        player = MediaPlayer.create( this, Settings.System.DEFAULT_ALARM_ALERT_URI);
        player.setLooping( true );
        player.start();
        return START_STICKY;
    }

    /* In case the service is deleted or crashes some how
    @Override
    public void onDestroy() {
        isServiceRunning = false;
        super.onDestroy();
    }*/

    @Override
    public void onDestroy() {
        super.onDestroy();
        player.stop();

        Intent broadcastIntent = new Intent();
        broadcastIntent.setAction("restartservice");
        broadcastIntent.setClass(this, Restarter.class);
        this.sendBroadcast(broadcastIntent);
    }

    @Override
    public IBinder onBind(Intent intent) {
        Log.v(LOG_TAG, "in onBind");
        return null;
    }

    @RequiresApi(Build.VERSION_CODES.O)
    private void startMyOwnForeground()
    {
        String NOTIFICATION_CHANNEL_ID = "example.permanence";
        String channelName = "Background Service";
        NotificationChannel chan = new NotificationChannel(NOTIFICATION_CHANNEL_ID, channelName, NotificationManager.IMPORTANCE_NONE);
        chan.setLightColor(Color.BLUE);
        chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);

        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        assert manager != null;
        manager.createNotificationChannel(chan);

        Intent activityIntent = new Intent(this, MainActivity.class );
        activityIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        activityIntent.setAction(Intent.ACTION_MAIN);
        activityIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity (this, 0 , activityIntent , 0 ) ;

        Intent broadcastIntent = new Intent(this, NotificationReceiver.class);
        PendingIntent actionIntent = PendingIntent.getBroadcast( this, 0, broadcastIntent, 0);

        Bitmap icon = BitmapFactory.decodeResource(getResources(), R.drawable.my_icon);
        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID);
        Notification notification = notificationBuilder
                .setContentTitle(getResources().getString(R.string.app_name))
                .setTicker(getResources().getString(R.string.app_name))
                .setContentText(getResources().getString(R.string.my_string))
                .setSmallIcon(R.drawable.my_icon)
                .setLargeIcon(Bitmap.createScaledBitmap(icon, 128, 170, false))
                .setContentIntent(contentIntent)
                .addAction(R.mipmap.ic_launcher, "Stop & Hide Notification", actionIntent)
                .setAutoCancel(true)
                .setOngoing(true)
                .build();
        startForeground(2, notification);
    }


    /*public String getCPUUsage() {
        String cpuUse = String.valueOf(myCPUInfo.readCpuFreqNow());
        return cpuUse;
    }*/

}

