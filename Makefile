PROTOC_GEN_GO := $(shell which protoc-gen-go)
PROTOC_GEN_GO_GRPC := $(shell which protoc-gen-go-grpc)

.PHONY: proto clean build

proto:
	@echo "Generating Protobuf files..."
	@mkdir -p internal/proto
	@find api/Protobuf -name "*.proto" -print0 | xargs -0 protoc \
		--proto_path=api \
		--go_out=internal/proto \
		--go_opt=paths=source_relative \
		--go-grpc_out=internal/proto \
		--go-grpc_opt=paths=source_relative \
		--go_opt=MProtobuf/Client/AuditScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go_opt=MProtobuf/Client/ClientCommandDeliverScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go_opt=MProtobuf/Client/ClientRegisterCsReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go_opt=MProtobuf/Client/ConfigUploadScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go_opt=MProtobuf/Client/HandshakeScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go_opt=MProtobuf/Command/GetClientConfig.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go_opt=MProtobuf/Command/HeartBeat.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go_opt=MProtobuf/Command/SendNotification.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go_opt=MProtobuf/Enum/AuditEvents.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go_opt=MProtobuf/Enum/CommandTypes.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go_opt=MProtobuf/Enum/ConfigTypes.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go_opt=MProtobuf/Enum/ListItemUpdateOperations.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go_opt=MProtobuf/Enum/Retcode.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go_opt=MProtobuf/Server/AuditScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go_opt=MProtobuf/Server/ClientCommandDeliverScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go_opt=MProtobuf/Server/ClientRegisterScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go_opt=MProtobuf/Server/ConfigUploadScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go_opt=MProtobuf/Server/HandshakeScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go_opt=MProtobuf/Service/Audit.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go_opt=MProtobuf/Service/ClientCommandDeliver.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go_opt=MProtobuf/Service/ClientRegister.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go_opt=MProtobuf/Service/ConfigUpload.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go_opt=MProtobuf/Service/Handshake.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go_opt=MProtobuf/AuditEvent/AppCrashed.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/AppSettingsUpdated.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/AuthorizeEvent.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/ClassChangeCompleted.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/PluginInstalled.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/PluginUninstalled.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go_opt=MProtobuf/AuditEvent/ProfileItemUpdated.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/Client/AuditScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go-grpc_opt=MProtobuf/Client/ClientCommandDeliverScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go-grpc_opt=MProtobuf/Client/ClientRegisterCsReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go-grpc_opt=MProtobuf/Client/ConfigUploadScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go-grpc_opt=MProtobuf/Client/HandshakeScReq.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Client \
		--go-grpc_opt=MProtobuf/Command/GetClientConfig.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go-grpc_opt=MProtobuf/Command/HeartBeat.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go-grpc_opt=MProtobuf/Command/SendNotification.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Command \
		--go-grpc_opt=MProtobuf/Enum/AuditEvents.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go-grpc_opt=MProtobuf/Enum/CommandTypes.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go-grpc_opt=MProtobuf/Enum/ConfigTypes.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go-grpc_opt=MProtobuf/Enum/ListItemUpdateOperations.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go-grpc_opt=MProtobuf/Enum/Retcode.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum \
		--go-grpc_opt=MProtobuf/Server/AuditScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go-grpc_opt=MProtobuf/Server/ClientCommandDeliverScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go-grpc_opt=MProtobuf/Server/ClientRegisterScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go-grpc_opt=MProtobuf/Server/ConfigUploadScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go-grpc_opt=MProtobuf/Server/HandshakeScRsp.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Server \
		--go-grpc_opt=MProtobuf/Service/Audit.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go-grpc_opt=MProtobuf/Service/ClientCommandDeliver.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go-grpc_opt=MProtobuf/Service/ClientRegister.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go-grpc_opt=MProtobuf/Service/ConfigUpload.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go-grpc_opt=MProtobuf/Service/Handshake.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service \
		--go-grpc_opt=MProtobuf/AuditEvent/AppCrashed.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/AppSettingsUpdated.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/AuthorizeEvent.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/ClassChangeCompleted.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/PluginInstalled.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/PluginUninstalled.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent \
		--go-grpc_opt=MProtobuf/AuditEvent/ProfileItemUpdated.proto=github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/AuditEvent

clean:
	rm -rf internal/proto

build:
	go build -o cims_server ./cmd/cims/main.go
