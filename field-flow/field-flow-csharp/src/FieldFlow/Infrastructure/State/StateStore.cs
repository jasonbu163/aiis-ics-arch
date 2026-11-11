// SQLite 连接仅由一个有界工作线程使用，派发事实与结果按事务持久化。
using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using FieldFlow.Domain;
using Microsoft.Data.Sqlite;

namespace FieldFlow.Infrastructure.State;

public sealed class StateStore : IDisposable
{
    private const string Database = "state.sqlite3";
    private readonly BlockingCollection<Action<SqliteConnection>> work = new(32);
    private readonly Thread worker;
    private readonly SqliteConnection connection;
    private readonly FileStream lockFile;
    private readonly string mode;

    private StateStore(string directory, string mode, string instance)
    {
        this.mode = mode;
        if (!Directory.Exists(directory)) throw new ConfigException("state_missing");
        lockFile = new FileStream(Path.Combine(directory, "writer.lock"), FileMode.Open,
            FileAccess.ReadWrite, FileShare.None);
        SqliteConnection? opened = null;
        try
        {
            opened = Connect(Path.Combine(directory, Database), SqliteOpenMode.ReadWrite);
            var meta = ReadMeta(opened);
            if (!meta.TryGetValue("schema_version", out var schema) || schema != "1" ||
                !meta.TryGetValue("implementation", out var implementation) || implementation != "csharp" ||
                !meta.TryGetValue("mode", out var storedMode) || storedMode != mode ||
                !meta.TryGetValue("instance_id", out var storedInstance) || storedInstance != instance)
                throw new ConfigException("state_identity");
            ConfigureWriter(opened);
            connection = opened;
            Recover(connection);
            worker = new Thread(Run) { IsBackground = true, Name = "ff-state-writer" };
            worker.Start();
        }
        catch
        {
            opened?.Dispose();
            lockFile.Dispose();
            throw;
        }
    }

    public static void Initialize(string directory, string mode, string instance)
    {
        if (mode is not ("dry_run" or "execute")) throw new ConfigException("state_mode");
        var full = Path.GetFullPath(directory);
        if (Directory.Exists(full) || File.Exists(full) || !Directory.Exists(Path.GetDirectoryName(full)))
            throw new ConfigException("state_exists");
        Directory.CreateDirectory(full);
        using var lockFile = new FileStream(Path.Combine(full, "writer.lock"), FileMode.CreateNew,
            FileAccess.ReadWrite, FileShare.None);
        var databasePath = Path.Combine(full, Database);
        using (new FileStream(databasePath, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { }
        using var connection = Connect(databasePath, SqliteOpenMode.ReadWrite);
        ConfigureWriter(connection);
        using var command = connection.CreateCommand();
        command.CommandText = """
            CREATE TABLE store_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE commands (
                source_id TEXT NOT NULL, command_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
                flow_id TEXT NOT NULL, device_id TEXT NOT NULL, point_id TEXT NOT NULL,
                host TEXT NOT NULL, port INTEGER NOT NULL, rack INTEGER NOT NULL, slot INTEGER NOT NULL,
                db INTEGER NOT NULL, offset INTEGER NOT NULL, value INTEGER NOT NULL,
                issued_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL,
                status TEXT NOT NULL, dispatch_count INTEGER NOT NULL, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL, PRIMARY KEY(source_id, command_id));
            CREATE TABLE command_events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, command_id TEXT NOT NULL,
                previous TEXT, current TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL);
            """;
        command.ExecuteNonQuery();
        foreach (var item in new Dictionary<string, string>
        {
            ["schema_version"] = "1", ["implementation"] = "csharp", ["mode"] = mode,
            ["instance_id"] = instance, ["store_uuid"] = Guid.NewGuid().ToString(),
            ["created_at"] = ProjectTime.Now()
        })
        {
            using var insert = connection.CreateCommand();
            insert.CommandText = "INSERT INTO store_meta(key,value) VALUES ($k,$v)";
            insert.Parameters.AddWithValue("$k", item.Key);
            insert.Parameters.AddWithValue("$v", item.Value);
            insert.ExecuteNonQuery();
        }
    }

    public static StateStore Open(string directory, string mode, string instance) => new(directory, mode, instance);

    public static object Inspect(string directory)
    {
        using var db = Connect(Path.Combine(Path.GetFullPath(directory), Database), SqliteOpenMode.ReadOnly);
        var counts = new Dictionary<string, long>();
        using (var command = db.CreateCommand())
        {
            command.CommandText = "SELECT status,COUNT(*) FROM commands GROUP BY status";
            using var reader = command.ExecuteReader();
            while (reader.Read()) counts[reader.GetString(0)] = reader.GetInt64(1);
        }
        var unresolved = new List<object>();
        using (var command = db.CreateCommand())
        {
            command.CommandText = """
                SELECT source_id,command_id,device_id,point_id,db,offset,status
                FROM commands WHERE status IN ('pending','in_flight','unknown')
                ORDER BY created_at LIMIT 65
                """;
            using var reader = command.ExecuteReader();
            while (reader.Read())
                unresolved.Add(new
                {
                    source_id = reader.GetString(0), command_id = reader.GetString(1),
                    device_id = reader.GetString(2), point_id = reader.GetString(3),
                    db = reader.GetInt32(4), offset = reader.GetInt32(5), status = reader.GetString(6)
                });
        }
        var truncated = unresolved.Count > 64;
        if (truncated) unresolved.RemoveAt(64);
        return new { meta = ReadMeta(db), counts, unresolved, unresolved_truncated = truncated };
    }

    public Task<string> AdmitAsync(Command intent) => ExecuteAsync(db =>
    {
        using var tx = db.BeginTransaction();
        using var existing = db.CreateCommand();
        existing.Transaction = tx;
        existing.CommandText = "SELECT fingerprint,status FROM commands WHERE source_id=$source AND command_id=$id";
        Identity(existing, intent);
        using (var reader = existing.ExecuteReader())
        {
            if (reader.Read())
            {
                var status = reader.GetString(1);
                if (reader.GetString(0) != Fingerprint(intent)) status = "identity_conflict";
                reader.Close();
                tx.Commit();
                return status;
            }
        }
        if (HasUnknown(db, tx, intent))
        {
            tx.Commit();
            return "unknown_blocked";
        }
        using var insert = db.CreateCommand();
        insert.Transaction = tx;
        insert.CommandText = """
            INSERT INTO commands(source_id,command_id,fingerprint,flow_id,device_id,point_id,
                host,port,rack,slot,db,offset,value,issued_at_ms,expires_at_ms,status,dispatch_count,created_at,updated_at)
            VALUES($source,$id,$fingerprint,$flow,$device,$point,$host,$port,$rack,$slot,$db,$offset,
                $value,$issued,$expires,'pending',0,$now,$now)
            """;
        Identity(insert, intent);
        Physical(insert, intent);
        insert.Parameters.AddWithValue("$fingerprint", Fingerprint(intent));
        insert.Parameters.AddWithValue("$flow", intent.FlowId);
        insert.Parameters.AddWithValue("$device", intent.DeviceId);
        insert.Parameters.AddWithValue("$point", intent.PointId);
        insert.Parameters.AddWithValue("$value", intent.Value);
        insert.Parameters.AddWithValue("$issued", intent.IssuedAtMs);
        insert.Parameters.AddWithValue("$expires", intent.ExpiresAtMs);
        insert.Parameters.AddWithValue("$now", ProjectTime.Now());
        insert.ExecuteNonQuery();
        Event(db, tx, intent.SourceId, intent.CommandId, null, "pending", "intent");
        tx.Commit();
        return "pending";
    });

    public Task<bool> DispatchAsync(Command intent) => ExecuteAsync(db =>
    {
        using var tx = db.BeginTransaction();
        if (HasUnknown(db, tx, intent)) { tx.Commit(); return false; }
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = """
            UPDATE commands SET status='in_flight',dispatch_count=1,updated_at=$now
            WHERE source_id=$source AND command_id=$id AND status='pending' AND dispatch_count=0
            """;
        Identity(command, intent);
        command.Parameters.AddWithValue("$now", ProjectTime.Now());
        var changed = command.ExecuteNonQuery() == 1;
        if (changed) Event(db, tx, intent.SourceId, intent.CommandId, "pending", "in_flight", "dispatch_permit");
        tx.Commit();
        return changed;
    });

    public Task TransitionAsync(Command intent, string from, string to, string reason) => ExecuteAsync(db =>
    {
        using var tx = db.BeginTransaction();
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = "UPDATE commands SET status=$to,updated_at=$now WHERE source_id=$source AND command_id=$id AND status=$from";
        Identity(command, intent);
        command.Parameters.AddWithValue("$to", to);
        command.Parameters.AddWithValue("$from", from);
        command.Parameters.AddWithValue("$now", ProjectTime.Now());
        if (command.ExecuteNonQuery() != 1) throw new InvalidOperationException("state_transition");
        Event(db, tx, intent.SourceId, intent.CommandId, from, to, reason);
        tx.Commit();
        return true;
    });

    public Task<bool> CancelPendingAsync(Command intent, string to, string reason) => ExecuteAsync(db =>
    {
        using var tx = db.BeginTransaction();
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = """
            UPDATE commands SET status=$to,updated_at=$now
            WHERE source_id=$source AND command_id=$id AND status='pending' AND dispatch_count=0
            """;
        Identity(command, intent);
        command.Parameters.AddWithValue("$to", to);
        command.Parameters.AddWithValue("$now", ProjectTime.Now());
        var changed = command.ExecuteNonQuery() == 1;
        if (changed) Event(db, tx, intent.SourceId, intent.CommandId, "pending", to, reason);
        tx.Commit();
        return changed;
    });

    private static bool HasUnknown(SqliteConnection db, SqliteTransaction tx, Command intent)
    {
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = """
            SELECT 1 FROM commands WHERE status='unknown' AND host=$host AND port=$port
                AND rack=$rack AND slot=$slot AND db=$db AND offset < $offset + 2 AND offset + 2 > $offset LIMIT 1
            """;
        Physical(command, intent);
        return command.ExecuteScalar() is not null;
    }

    private static void Physical(SqliteCommand sql, Command intent)
    {
        sql.Parameters.AddWithValue("$host", intent.Plc.Host);
        sql.Parameters.AddWithValue("$port", intent.Plc.Port);
        sql.Parameters.AddWithValue("$rack", intent.Plc.Rack);
        sql.Parameters.AddWithValue("$slot", intent.Plc.Slot);
        sql.Parameters.AddWithValue("$db", intent.Point.Db);
        sql.Parameters.AddWithValue("$offset", intent.Point.Offset);
    }

    private static void Identity(SqliteCommand sql, Command intent)
    {
        sql.Parameters.AddWithValue("$source", intent.SourceId);
        sql.Parameters.AddWithValue("$id", intent.CommandId);
    }

    private static string Fingerprint(Command intent)
    {
        var text = JsonSerializer.Serialize(new
        {
            intent.FlowId, intent.BusinessName, intent.DeviceId, intent.PointId,
            intent.Plc.Host, intent.Plc.Port, intent.Plc.Rack, intent.Plc.Slot,
            intent.Point.Db, intent.Point.Size, intent.Point.Offset,
            intent.Value, intent.IssuedAtMs, intent.ExpiresAtMs, intent.IntervalMs,
            intent.InputMaxAgeMs, intent.GetUrl
        });
        return Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(text)));
    }

    private static void Event(SqliteConnection db, SqliteTransaction tx, string source, string id,
        string? previous, string current, string reason)
    {
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = """
            INSERT INTO command_events(source_id,command_id,previous,current,reason,created_at)
            VALUES($source,$id,$previous,$current,$reason,$now)
            """;
        command.Parameters.AddWithValue("$source", source);
        command.Parameters.AddWithValue("$id", id);
        command.Parameters.AddWithValue("$previous", (object?)previous ?? DBNull.Value);
        command.Parameters.AddWithValue("$current", current);
        command.Parameters.AddWithValue("$reason", reason);
        command.Parameters.AddWithValue("$now", ProjectTime.Now());
        command.ExecuteNonQuery();
    }

    private static void Recover(SqliteConnection db)
    {
        using var tx = db.BeginTransaction();
        using var command = db.CreateCommand();
        command.Transaction = tx;
        command.CommandText = "SELECT source_id,command_id FROM commands WHERE status='in_flight'";
        var pending = new List<(string Source, string Id)>();
        using (var reader = command.ExecuteReader())
            while (reader.Read()) pending.Add((reader.GetString(0), reader.GetString(1)));
        foreach (var (source, id) in pending)
        {
            using var update = db.CreateCommand();
            update.Transaction = tx;
            update.CommandText = "UPDATE commands SET status='unknown',updated_at=$now WHERE source_id=$source AND command_id=$id AND status='in_flight'";
            update.Parameters.AddWithValue("$now", ProjectTime.Now());
            update.Parameters.AddWithValue("$source", source);
            update.Parameters.AddWithValue("$id", id);
            update.ExecuteNonQuery();
            Event(db, tx, source, id, "in_flight", "unknown", "restart_recovery");
        }
        tx.Commit();
    }

    private static SqliteConnection Connect(string path, SqliteOpenMode mode)
    {
        var db = new SqliteConnection(new SqliteConnectionStringBuilder
        {
            DataSource = path, Mode = mode, Pooling = false, DefaultTimeout = 1
        }.ToString());
        try
        {
            db.Open();
            return db;
        }
        catch
        {
            db.Dispose();
            throw;
        }
    }

    private static void ConfigureWriter(SqliteConnection db)
    {
        using var command = db.CreateCommand();
        command.CommandText = "PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=500";
        command.ExecuteNonQuery();
    }

    private static Dictionary<string, string> ReadMeta(SqliteConnection db)
    {
        using var command = db.CreateCommand();
        command.CommandText = "SELECT key,value FROM store_meta";
        using var reader = command.ExecuteReader();
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        while (reader.Read()) result.Add(reader.GetString(0), reader.GetString(1));
        return result;
    }

    private Task<T> ExecuteAsync<T>(Func<SqliteConnection, T> operation)
    {
        var completion = new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously);
        if (!work.TryAdd(db =>
        {
            try { completion.SetResult(operation(db)); }
            catch (Exception error) { completion.SetException(error); }
        })) throw new IOException("state_queue_full");
        return completion.Task;
    }

    private void Run()
    {
        try { foreach (var job in work.GetConsumingEnumerable()) job(connection); }
        finally { connection.Dispose(); }
    }

    public bool TryClose(TimeSpan timeout)
    {
        work.CompleteAdding();
        if (!worker.Join(timeout)) return false;
        work.Dispose();
        lockFile.Dispose();
        return true;
    }

    public void Dispose() => TryClose(TimeSpan.FromSeconds(15));
}
