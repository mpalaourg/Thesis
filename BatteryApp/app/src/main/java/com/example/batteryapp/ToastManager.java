package com.example.batteryapp;

import android.content.Context;
import android.widget.Toast;

public class ToastManager {

    private static Toast myCurrentToast;

    /** This method keeps track of the Toast Object used by the Activity. To avoid a Toast message
     *  to wait for the previous one to end, if present the previous Toast message will be cancelled
     *  and a new message will be appeared.
     *
     * @param ctx  -> The context to use.
     * @param text -> The text to be displayed of the Toast.
     */
    public static void showToast(Context ctx, String text)
    {
        try {
            if (myCurrentToast != null) {
                myCurrentToast.cancel();
            }
            myCurrentToast = Toast.makeText(ctx, text, Toast.LENGTH_LONG);
            myCurrentToast.show();
        }catch(Exception ex){
            ex.printStackTrace();
        }
    }

    /**
     * This method will dismiss the Toast object -if present-, when the user exit the app.
     */
    public static void dismissToast(){
        if(myCurrentToast != null){
            myCurrentToast.cancel();
        }
    }
}
