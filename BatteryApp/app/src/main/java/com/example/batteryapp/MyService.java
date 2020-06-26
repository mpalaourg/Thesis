package com.example.batteryapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.os.Build;
import android.os.IBinder;

import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;

import java.util.Timer;
import java.util.TimerTask;

public class MyService extends Service {
    Timer timer = new Timer();
    CPU_Info myCPUInfo = new CPU_Info();

    /** Function which is called at the creation of the Service. For androids version after O
     *  will a create a foreground service with a notification, where the proper notification channel
     *  is initialized. Otherwise, the service has a simple notification.
     */
    @Override
    public void onCreate() {
        super.onCreate();
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.O)
            startMyOwnForeground();
        else
            startForeground(1, new Notification());
    }

    /**
     *
     * @param intent  -> The Intent supplied to Context.startService(Intent), as given.
     * @param flags   -> Additional data about this start request. Value is either 0 or a combination of START_FLAG_REDELIVERY, and START_FLAG_RETRY
     * @param startId -> A unique integer representing this specific request to start.
     * @return
     */
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        final MainActivity currActivity = new MainActivity();
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                int usage = getCPUUsage();
                currActivity.setCPUbar(usage);
            }
        }, 0, 10000);
        return START_STICKY;
    }

    /* In case the service is deleted or crashes some how
    @Override
    public void onDestroy() {
        isServiceRunning = false;
        super.onDestroy();
    }*/

    /** Function which is called before the Service exit and close. Clean up business must be
     * done here
     */
    @Override
    public void onDestroy() {
        super.onDestroy();
        timer.cancel();
    }

    /** Function to used if clients want to bind the service.
     * Return the communication channel to the service.
     * @param intent -> The Intent that was used to bind to this service.
     * @return null (no binding needed)
     */
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /** Function to start my own Foreground Service. At first, the channel for the notification
     * must be initialized. Then, the notification is created, with proper title, icons and an activity
     * intent, so the user can by clicking the notification to open the (already open) app.
     */
    @RequiresApi(Build.VERSION_CODES.O)
    private void startMyOwnForeground()  {
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

        Bitmap icon = BitmapFactory.decodeResource(getResources(), R.drawable.my_icon);
        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID);
        Notification notification = notificationBuilder
                .setContentTitle(getResources().getString(R.string.app_name))
                .setTicker(getResources().getString(R.string.app_name))
                .setContentText(getResources().getString(R.string.my_string))
                .setSmallIcon(R.drawable.my_icon)
                .setLargeIcon(Bitmap.createScaledBitmap(icon, 128, 170, false))
                .setContentIntent(contentIntent)
                .setAutoCancel(true)
                .setOngoing(true)
                .build();
        startForeground(2, notification);
    }


    public int getCPUUsage() {
        int cpuUse = (int) myCPUInfo.readCpuPercentNow();
        System.out.println("Current CPU Usage: " + cpuUse + " - " + System.currentTimeMillis());
        return cpuUse;
    }

}

