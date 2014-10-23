/* DO NOT EDIT THIS FILE - it is machine generated */
#include <jni.h>
/* Header for class xmipp_Filename */

#ifndef _Included_xmipp_jni_PickingClassifier
#define _Included_xmipp_jni_PickingClassifier
#ifdef __cplusplus
extern "C" {
#endif


JNIEXPORT void JNICALL
Java_xmipp_jni_PickingClassifier_create(JNIEnv *env, jobject jobj, jint, jstring, jstring);



JNIEXPORT void JNICALL
Java_xmipp_jni_PickingClassifier_destroy(JNIEnv *env, jobject jobj);


JNIEXPORT void JNICALL Java_xmipp_jni_PickingClassifier_autopick
  (JNIEnv *, jobject, jstring, jobject, jint percent);



JNIEXPORT void JNICALL Java_xmipp_jni_PickingClassifier_correct
  (JNIEnv *, jobject, jobjectArray, jobjectArray);

JNIEXPORT void JNICALL Java_xmipp_jni_PickingClassifier_train
  (JNIEnv *, jobject, jobject, jint x, jint y, jint width, jint height);

JNIEXPORT void JNICALL Java_xmipp_jni_PickingClassifier_setSize
(JNIEnv *env, jobject jobj, jint psize);


JNIEXPORT jint JNICALL Java_xmipp_jni_PickingClassifier_getParticlesThreshold
(JNIEnv *env, jobject jobj);


#ifdef __cplusplus
}
#endif
#endif
