import authService from "@/lib/services/authService";
import { router } from "expo-router";
import { useState } from "react";
import { Alert, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async () => {
        // Validate inputs
        if (!username.trim() || !password.trim()) {
            Alert.alert("Error", "Username and password are required");
            return;
        }

        setIsLoading(true);

        try {
            const loginData = {
                username: username,
                password: password
            };

            // Call authService login method
            await authService.login(loginData);

            Alert.alert("Success", "Logged in successfully!", [
                { text: "OK", onPress: () => router.back() }
            ]);
        } catch (error) {
            Alert.alert("Error", "Failed to log in. Please check your credentials.");
            console.error("Login error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView
                contentContainerStyle={styles.scrollContent}
                keyboardShouldPersistTaps="handled"
            >
                <Text style={styles.title}>Welcome Back</Text>
                <Text style={styles.subtitle}>Log in to your account</Text>

                <View style={styles.formContainer}>
                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Username</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Enter your username"
                            value={username}
                            onChangeText={setUsername}
                            autoCapitalize="none"
                            autoCorrect={false}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Password</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Enter your password"
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                            autoCapitalize="none"
                            autoCorrect={false}
                        />
                    </View>

                    <Pressable
                        style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
                        onPress={handleLogin}
                        disabled={isLoading}
                    >
                        <Text style={styles.submitButtonText}>
                            {isLoading ? "Logging In..." : "Log In"}
                        </Text>
                    </Pressable>

                    <Pressable
                        style={styles.signupLink}
                        onPress={() => router.replace('/(auth)/signup')}
                    >
                        <Text style={styles.signupLinkText}>
                            Don&apos;t have an account? <Text style={styles.signupLinkBold}>Sign Up</Text>
                        </Text>
                    </Pressable>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F2F2F7',
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'flex-start',
        paddingHorizontal: 20,
        paddingVertical: 60,
    },
    title: {
        fontSize: 34,
        fontWeight: 'bold',
        color: '#000',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 17,
        color: '#6D6D72',
        marginBottom: 40,
    },
    formContainer: {
        width: '100%',
    },
    inputContainer: {
        marginBottom: 20,
    },
    label: {
        fontSize: 15,
        fontWeight: '600',
        color: '#000',
        marginBottom: 8,
    },
    input: {
        backgroundColor: 'white',
        borderRadius: 10,
        paddingHorizontal: 16,
        paddingVertical: 12,
        fontSize: 17,
        borderWidth: 1,
        borderColor: '#E5E5EA',
    },
    submitButton: {
        backgroundColor: '#007AFF',
        borderRadius: 10,
        paddingVertical: 16,
        alignItems: 'center',
        marginTop: 10,
    },
    submitButtonDisabled: {
        backgroundColor: '#A0CFFF',
    },
    submitButtonText: {
        color: 'white',
        fontSize: 17,
        fontWeight: '600',
    },
    signupLink: {
        marginTop: 20,
        alignItems: 'center',
    },
    signupLinkText: {
        fontSize: 15,
        color: '#6D6D72',
    },
    signupLinkBold: {
        color: '#007AFF',
        fontWeight: '600',
    },
});
