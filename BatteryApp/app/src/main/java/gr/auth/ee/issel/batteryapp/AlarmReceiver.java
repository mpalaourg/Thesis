package gr.auth.ee.issel.batteryapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.os.Build;

import androidx.core.app.NotificationCompat;

import gr.auth.ee.issel.batteryapp.R;

public class AlarmReceiver extends BroadcastReceiver {

    /** Show a one time notification to user to remind them to use the app once a day.
     *
     * @param context -> The Context in which the receiver is running.
     * @param intent  -> The Intent being received.
     */
    @Override
    public void onReceive(Context context, Intent intent) {
        Intent activityIntent = new Intent(context, MainActivity.class );
        activityIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        activityIntent.setAction(Intent.ACTION_MAIN);
        activityIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity (context, 0 , activityIntent , 0 ) ;
        Bitmap icon = BitmapFactory.decodeResource(context.getResources(), R.drawable.my_icon);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){
            String NOTIFICATION_CHANNEL_ID = "example.notification";
            String channelName = "Notification Reminder";
            NotificationChannel chan = new NotificationChannel(NOTIFICATION_CHANNEL_ID, channelName, NotificationManager.IMPORTANCE_HIGH);
            chan.setLightColor(Color.BLUE);
            chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);

            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            assert manager != null;
            manager.createNotificationChannel(chan);

            NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(context, NOTIFICATION_CHANNEL_ID);
            Notification notification = notificationBuilder
                    .setContentTitle(context.getResources().getString(R.string.app_name))
                    .setTicker(context.getResources().getString(R.string.app_name))
                    .setContentText(context.getResources().getString(R.string.NotificationString))
                    .setSmallIcon(R.drawable.my_icon)
                    .setLargeIcon(Bitmap.createScaledBitmap(icon, 128, 170, false))
                    .setContentIntent(contentIntent)
                    .setAutoCancel(true)
                    .setOngoing(false)
                    .build();
            manager.notify(3 , notification);

        } else {
            /* For android below 8.0 . Not tested yet*/
            Notification.Builder notificationBuilder = new Notification.Builder(context);
            Notification notification = notificationBuilder
                    .setContentTitle(context.getResources().getString(R.string.app_name))
                    .setTicker(context.getResources().getString(R.string.app_name))
                    .setContentText(context.getResources().getString(R.string.NotificationString))
                    .setSmallIcon(R.drawable.my_icon)
                    .setLargeIcon(Bitmap.createScaledBitmap(icon, 128, 170, false))
                    .setContentIntent(contentIntent)
                    .setAutoCancel(true)
                    .setOngoing(false)
                    .build();
            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            assert manager != null;
            manager.notify(4, notification);
        }

    }

}
