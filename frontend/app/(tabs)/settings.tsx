import { View, Text, StyleSheet, Pressable } from "react-native";
import { router } from "expo-router";
import Ionicons from '@expo/vector-icons/Ionicons';

export default function Settings() {
    return (
        <View style={styles.container}>
            <Text style={styles.header}>Settings</Text>
            
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Account</Text>
                
                <Pressable 
                    style={styles.menuItem}
                    onPress={() => router.push('/(auth)/login')}
                >
                    <Ionicons name="log-in-outline" size={24} color="#007AFF" />
                    <Text style={styles.menuText}>Login</Text>
                    <Ionicons name="chevron-forward" size={20} color="#C7C7CC" />
                </Pressable>

                <Pressable 
                    style={styles.menuItem}
                    onPress={() => router.push('/(auth)/signup')}
                >
                    <Ionicons name="person-add-outline" size={24} color="#007AFF" />
                    <Text style={styles.menuText}>Sign Up</Text>
                    <Ionicons name="chevron-forward" size={20} color="#C7C7CC" />
                </Pressable>
            </View>
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F2F2F7',
    },
    header: {
        fontSize: 34,
        fontWeight: 'bold',
        paddingHorizontal: 20,
        paddingTop: 60,
        paddingBottom: 20,
        backgroundColor: '#F2F2F7',
    },
    section: {
        marginTop: 20,
        backgroundColor: 'white',
    },
    sectionTitle: {
        fontSize: 13,
        fontWeight: '600',
        color: '#6D6D72',
        paddingHorizontal: 20,
        paddingTop: 16,
        paddingBottom: 8,
        textTransform: 'uppercase',
        backgroundColor: '#F2F2F7',
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 20,
        backgroundColor: 'white',
        borderBottomWidth: StyleSheet.hairlineWidth,
        borderBottomColor: '#C7C7CC',
    },
    menuText: {
        flex: 1,
        fontSize: 17,
        marginLeft: 15,
        color: '#000',
    },
});
