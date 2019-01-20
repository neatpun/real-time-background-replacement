package net.simplifiedcoding.videoupload;

import static android.util.TypedValue.COMPLEX_UNIT_SP;

import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnShowListener;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.location.Address;
import android.net.Uri;
import android.support.annotation.NonNull;
import android.support.v4.widget.CircularProgressDrawable;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AlertDialog.Builder;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.TextView;
import com.google.gson.GsonBuilder;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.security.SecureRandom;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class Utils {

  private static final String TAG = Utils.class.getSimpleName() + " YOYO";

  public static CircularProgressDrawable getProgressDrawable(Context context) {
    CircularProgressDrawable circularProgressDrawable = new CircularProgressDrawable(context);
    circularProgressDrawable.setStrokeWidth(6f);
    circularProgressDrawable.setCenterRadius(30f);
    circularProgressDrawable.setColorSchemeColors(context.getResources().getIntArray(R.array.gplus_colors));
//    circularProgressDrawable.sets
//        .sweepSpeed(mSpeed)
//        .rotationSpeed(mSpeed)
    circularProgressDrawable.start();
    return circularProgressDrawable;
  }

  public static CircularProgressDrawable getBlackProgressDrawable(Context context) {
    CircularProgressDrawable circularProgressDrawable = new CircularProgressDrawable(context);
    circularProgressDrawable.setStrokeWidth(6f);
    circularProgressDrawable.setCenterRadius(30f);
    circularProgressDrawable.setColorSchemeColors(context.getResources().getColor(R.color.white));
    circularProgressDrawable.start();
    return circularProgressDrawable;
  }

  public static int dpToPx(int dp, Context context) {
    float scale = context.getResources().getDisplayMetrics().density;
    return ((int) (dp * scale + 0.5f));
  }


}

