package net.simplifiedcoding.videoupload;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.DialogFragment;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import com.bumptech.glide.Glide;

public class DialogProgress extends DialogFragment {

  public static final String TAG = DialogProgress.class.getSimpleName() + " YOYO";
  private String title;

  private TextView tv;

  public static DialogProgress newInstance() {
    return new DialogProgress();
  }

  public static DialogProgress newInstance(String title){
    DialogProgress dialogProgress = new DialogProgress();
    Bundle bundle = new Bundle();
    bundle.putString("title", title);
    dialogProgress.setArguments(bundle);
    return dialogProgress;
  }

  public DialogProgress(){
  }

  @NonNull
  @Override
  public Dialog onCreateDialog(final Bundle savedInstanceState) {

    AlertDialog.Builder builder = new AlertDialog.Builder(getActivity(), R.style.DialogProgressStyle);
    builder.setCancelable(false);

    View view = getActivity().getLayoutInflater().inflate(R.layout.mprogress_dialog, null);

    Bundle arguments = getArguments();
    if(arguments!=null && arguments.containsKey("title")){
      title = arguments.getString("title");
    }

    tv = view.findViewById(R.id.title);
    if(title==null)
      tv.setVisibility(View.GONE);
    else {
      tv.setVisibility(View.VISIBLE);
      tv.setText(title);
    }

    ImageView imageView = view.findViewById(R.id.progress);
    Glide.with(getActivity())
        .load(Utils.getBlackProgressDrawable(getActivity()))
        .into(imageView);

    builder.setView(view);

    return builder.create();
  }

  public void setTitle(String title){
    if(title==null)
      tv.setVisibility(View.GONE);
    else {
      tv.setVisibility(View.VISIBLE);
      tv.setText(title);
    }
  }

  public void display(Context context) {
    if(!this.isShowing())
      show(((AppCompatActivity) context).getSupportFragmentManager(), null);
  }

  public void displayNow(Context context) {
    if(!this.isShowing())
      showNow(((AppCompatActivity) context).getSupportFragmentManager(), null);
  }

  public boolean isShowing() {
    if (getDialog() != null) {
      return getDialog().isShowing();
    } else {
      return false;
    }
  }

  public void done() {
    if (isShowing()) {
      dismiss();
    }
  }
}
